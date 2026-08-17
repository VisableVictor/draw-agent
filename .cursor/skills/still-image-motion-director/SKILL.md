---
name: still-image-motion-director
description: >-
  静图动效导演：分析一张静态图片，决定它应该动/微动/保持静止，
  锁定文字和纸张元素，输出可直接复制的图生视频 Prompt。
  Use when user mentions 图生视频、图片动起来、让图动、motion prompt、
  怎么动、锁住文字、即梦、Jimeng、i2v、image to video、
  这张图怎么做成视频、动效方向。
  前提条件：用户必须提供至少一张静态图片。
  不用于：从零生成图片、视频剪辑、视频脚本编写。
alwaysApply: false
globs: []
---

# GC Still Image Motion Director

Turn a still image into a motion decision and a copy-ready image-to-video prompt. Derive motion from the image's subject, meaning, composition, and physical relationships; do not apply a stock animation effect.

## Core Workflow

1. Inspect the real image before proposing motion.
   - For a folder, inventory readable image files, dimensions, names, and visual patterns. Create a contact sheet when it materially improves comparison.
   - If an image cannot be accessed, ask the user to attach or provide it again instead of inventing its contents.
2. Separate observation from recommendation.
   - State what is visibly present.
   - Label inferred meaning or motion intent as a recommendation, not a fact.
3. Identify:
   - primary subject;
   - subject type and implied behavior;
   - composition axis, focal point, whitespace, frames, and hierarchy;
   - text, numbers, paper texture, annotations, borders, and other fragile layout elements;
   - physical relationships such as gravity, tension, wind, water, contact, rotation, or resistance.
4. Decide whether the image should use:
   - `motion`: one clear restrained action;
   - `micro-motion`: an almost still action or environmental trace;
   - `static`: no subject motion; explain why stillness serves the image better.
5. Select at most:
   - one primary motion;
   - one physically related secondary motion;
   - one optional observation effect, only when justified.
6. Define the lock list before writing the prompt.
7. Write a platform-ready prompt with a concrete subject, path, range, timing, locks, and failure prohibitions.
8. Check that the proposal preserves the original design rather than regenerating it frame by frame.

Read [references/motion-decision-framework.md](references/motion-decision-framework.md) when the image's correct motion is ambiguous, when comparing several images, or when deciding that a subject should remain still.

Read [references/prompt-construction.md](references/prompt-construction.md) when writing the final prompt, adapting it to a named platform, or diagnosing why a previous prompt caused drift or deformation.

## Motion Rule

Let motion come from the image itself.

Prefer, in order:

1. an intrinsic action of the subject;
2. a physical response caused by that action;
3. an environmental or observation effect when the first two are unsuitable.

Do not default to scanning light, floating, breathing paper, parallax, particles, camera push-in, or generic cinematic motion. Do not force a specimen, stone, archive, paused mechanism, or quiet object to behave like a living subject. A valid result may recommend no subject movement.

Keep motion restrained unless the user explicitly asks for stronger animation. Use the smallest movement that makes the intended relationship legible.

## Stability Rules

- Lock typography, numbers, labels, handwritten notes, paper texture, borders, frames, grids, and collage geometry.
- Keep subjects inside their original visual region unless the composition clearly provides a path.
- Preserve subject count, identity, silhouette, clothing, proportions, and object connectivity.
- Keep ropes, handles, joints, stems, limbs, and mechanical links continuous.
- Avoid camera movement by default for poster, collage, archive, and editorial layouts.
- Do not describe unrelated styling that is already supplied by the source image; redundant style language can encourage redraw.
- For a motionless recommendation, propose a static export or a minimal environmental trace instead of inventing action.

## Output

For one image, return:

```markdown
图片：
[name]

画面观察：
[visible subject, composition, and fragile elements]

动态判断：
[motion / micro-motion / static] — [short reason]

建议运动：
- 主动作：
- 伴随动作：
- 范围与路径：
- 节奏与时长：

必须固定：
- [...]

不建议：
- [...]

可直接复制到[目标平台]：
[complete prompt]

主要风险：
- [...]
```

Omit empty fields. If the user asks for only a prompt, return only the copy-ready prompt.

For a folder or image set:

1. summarize the shared visual system;
2. state which constraints can be shared;
3. classify each image as `motion`, `micro-motion`, or `static`;
4. write a separate prompt for each requested image;
5. do not claim that one universal prompt is sufficient when subject behavior differs.

Default to Chinese when the user writes Chinese. Default to a restrained 4-second image-to-video clip when the target model and duration are not specified, and state that assumption briefly.

## Quality Check

Before delivering, verify:

- Is the motion caused by something visible in the image?
- Is there only one dominant action?
- Does the secondary motion obey the same physical cause?
- Are all fragile design elements explicitly locked?
- Does the prompt specify range, direction, and rhythm rather than saying only "move naturally"?
- Could the result still work if the camera never moves?
- Did you avoid making every image use the same effect?
- Did you mark uncertainty instead of presenting a guessed original prompt as fact?
