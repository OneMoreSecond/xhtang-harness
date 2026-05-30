from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from xhtang_harness.config import HarnessConfig
from xhtang_harness.errors import HarnessError
from xhtang_harness.providers.deepseek import DeepSeekMessage, DeepSeekOptions

_SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_MAX_PROMPT_SECTION_CHARS = 8_000


class SkillError(HarnessError):
    code = "skill_error"


@dataclass(frozen=True)
class LocalSkill:
    name: str
    description: str
    body: str
    path: Path


@dataclass(frozen=True)
class SkillReference:
    path: str
    content: str


@dataclass(frozen=True)
class SkillDecision:
    should_create: bool
    reason: str
    skill_name: str | None = None
    description: str | None = None
    skill_body: str | None = None
    references: tuple[SkillReference, ...] = ()


@dataclass(frozen=True)
class SkillWriteResult:
    skill_name: str
    target_path: Path
    file_count: int


def matching_skill_context(prompt: str, skills_path: Path) -> tuple[str | None, int]:
    matched = [
        skill
        for skill in _load_local_skills(skills_path)
        if _skill_matches_prompt(skill, prompt)
    ]
    if not matched:
        return None, 0

    sections = [
        (
            f"# Skill: {skill.name}\n"
            f"Description: {skill.description}\n"
            f"{skill.body.strip()}"
        )
        for skill in matched
    ]
    return (
        "Local skill instructions matched this prompt. Use them when relevant.\n\n"
        + "\n\n---\n\n".join(sections),
        len(matched),
    )


def build_reflection_messages(
    *,
    config: HarnessConfig,
    final_answer: str,
) -> tuple[DeepSeekMessage, DeepSeekMessage]:
    return (
        DeepSeekMessage(
            role="system",
            content=(
                "You decide whether a completed local harness task deserves a "
                "reusable skill. Return json only. Create a skill only when the "
                "task produced reusable workflow knowledge, not for one-off data."
            ),
        ),
        DeepSeekMessage(
            role="user",
            content=(
                "Return json with this shape:\n"
                "{\n"
                '  "should_create": true,\n'
                '  "reason": "short reason",\n'
                '  "skill_name": "lowercase-hyphen-name",\n'
                '  "description": "When this skill should be used.",\n'
                '  "skill_body": "Markdown instructions.",\n'
                '  "references": []\n'
                "}\n\n"
                f"Completed goal:\n{_truncate(config.prompt)}\n\n"
                f"Final answer:\n{_truncate(final_answer)}"
            ),
        ),
    )


def reflection_options(config: HarnessConfig) -> DeepSeekOptions:
    return DeepSeekOptions(
        model=config.model,
        thinking="disabled",
        reasoning_effort=None,
        temperature=0.2,
        max_tokens=4096,
        user_id=config.user_id,
        response_format={"type": "json_object"},
    )


def parse_skill_decision(content: str) -> SkillDecision:
    try:
        raw = json.loads(content)
    except json.JSONDecodeError as error:
        raise SkillError("skill reflection returned malformed JSON") from error

    if not isinstance(raw, dict):
        raise SkillError("skill reflection JSON must be an object")

    should_create = raw.get("should_create")
    if not isinstance(should_create, bool):
        raise SkillError("skill reflection requires boolean should_create")

    reason = _required_string(raw, "reason")
    if not should_create:
        return SkillDecision(should_create=False, reason=reason)

    references = tuple(_references_from(raw.get("references", [])))
    return SkillDecision(
        should_create=True,
        reason=reason,
        skill_name=_required_string(raw, "skill_name"),
        description=_required_string(raw, "description"),
        skill_body=_required_string(raw, "skill_body"),
        references=references,
    )


def write_skill(decision: SkillDecision, skills_path: Path) -> SkillWriteResult:
    if not decision.should_create:
        raise SkillError("cannot write a skipped skill decision")
    if decision.skill_name is None:
        raise SkillError("skill decision is missing skill_name")
    if decision.description is None:
        raise SkillError("skill decision is missing description")
    if decision.skill_body is None:
        raise SkillError("skill decision is missing skill_body")
    if not _SKILL_NAME_PATTERN.fullmatch(decision.skill_name):
        raise SkillError("skill_name must use lowercase letters, digits, and hyphens")

    target_path = skills_path / decision.skill_name
    if target_path.exists():
        raise SkillError(f"skill already exists: {decision.skill_name}")

    temp_root = skills_path.parent / ".xhtang-harness" / "tmp" / "skills"
    temp_path = temp_root / f"{decision.skill_name}-{uuid4().hex}"
    try:
        temp_path.mkdir(parents=True, exist_ok=False)
        _write_text(
            temp_path / "SKILL.md",
            _skill_file_content(
                name=decision.skill_name,
                description=decision.description,
                body=decision.skill_body,
            ),
        )
        file_count = 1
        for reference in decision.references:
            reference_path = _validated_reference_path(reference.path)
            _write_text(temp_path / reference_path, reference.content)
            file_count += 1

        skills_path.mkdir(parents=True, exist_ok=True)
        temp_path.rename(target_path)
    except OSError as error:
        raise SkillError(f"could not write skill: {error}") from error
    finally:
        if temp_path.exists():
            shutil.rmtree(temp_path)

    return SkillWriteResult(
        skill_name=decision.skill_name,
        target_path=target_path,
        file_count=file_count,
    )


def _load_local_skills(skills_path: Path) -> tuple[LocalSkill, ...]:
    if not skills_path.exists():
        return ()
    if not skills_path.is_dir():
        return ()

    skills: list[LocalSkill] = []
    for skill_file in sorted(skills_path.glob("*/SKILL.md")):
        skill = _read_local_skill(skill_file)
        if skill is not None:
            skills.append(skill)
    return tuple(skills)


def _read_local_skill(skill_file: Path) -> LocalSkill | None:
    try:
        content = skill_file.read_text(encoding="utf-8")
    except OSError:
        return None

    lines = content.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return None
    end_index = _frontmatter_end_index(lines)
    if end_index is None:
        return None

    frontmatter = _frontmatter_fields(lines[1:end_index])
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if name is None or description is None:
        return None

    body = "\n".join(lines[end_index + 1 :]).strip()
    if not body:
        return None
    return LocalSkill(
        name=name,
        description=description,
        body=body,
        path=skill_file,
    )


def _frontmatter_end_index(lines: list[str]) -> int | None:
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return index
    return None


def _frontmatter_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in lines:
        key, separator, value = line.partition(":")
        if not separator:
            continue
        normalized_key = key.strip()
        if normalized_key in {"name", "description"}:
            fields[normalized_key] = _strip_optional_quotes(value.strip())
    return fields


def _strip_optional_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _skill_matches_prompt(skill: LocalSkill, prompt: str) -> bool:
    prompt_text = prompt.casefold()
    return (
        skill.description.casefold() in prompt_text
        or skill.name.casefold() in prompt_text
    )


def _required_string(raw: dict[object, object], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SkillError(f"skill reflection requires non-empty string {key}")
    return value.strip()


def _references_from(raw: object) -> list[SkillReference]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise SkillError("skill reflection references must be a list")

    references: list[SkillReference] = []
    for item in raw:
        if not isinstance(item, dict):
            raise SkillError("skill reflection reference must be an object")
        references.append(
            SkillReference(
                path=_required_string(item, "path"),
                content=_required_string(item, "content"),
            )
        )
    return references


def _validated_reference_path(path: str) -> Path:
    reference_path = Path(path)
    if reference_path.is_absolute() or ".." in reference_path.parts:
        raise SkillError("skill reference path must stay inside the skill folder")
    if (
        len(reference_path.parts) != 2
        or reference_path.parts[0] != "references"
        or reference_path.suffix != ".md"
    ):
        raise SkillError("skill references must use references/*.md paths")
    return reference_path


def _skill_file_content(*, name: str, description: str, body: str) -> str:
    return f"---\nname: {name}\ndescription: {description}\n---\n\n{body.strip()}\n"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _truncate(value: str) -> str:
    if len(value) <= _MAX_PROMPT_SECTION_CHARS:
        return value
    return value[:_MAX_PROMPT_SECTION_CHARS] + "\n[truncated]"
