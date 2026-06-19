---
id: "2026-06-19-claudeに作らせた3d-wireframe-shooting-game-3dwfgpy-01"
title: "Claudeに作らせた3D wireframe shooting game '3dwfg.py'"
url: "https://qiita.com/fygar256/items/6518e4d1cac8107c8cae"
source: "qiita"
category: "ai-workflow"
tags: ["Python", "qiita"]
date_published: "2026-06-19"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

Claudeに作らせた、3D wireframe shooting gameです。ゲームデザインはしましたが、あっという間にコードを書いてくれる。作り込めば面白いものができそうです。

pygameを使っています。

矢印キーでパン、スペースでshot、[ESC]でquitです。ゲームオーバー時’R'でリトライです。

`python 3dwfg.py`で、実行です。

```text:3dwfg.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wireframe_fps3.py
  pygame ワイヤーフレーム 3D シューティング（視点パン方式）。

  仕様:
    - 照準は画面中心に固定
    - 移動キー(矢印 / WASD)で「画面全体」を逆方向へパンして視点を動かす
      （右を押すと画面は左へ動く＝右側の敵が中心へ寄る）
    - 当たり判定: 敵の画面座標が自分(中心)の座標と一致したときヒット
    - 床グリッドは廃止。流れる星はそのまま（前進感）

  敵3種:
    DRONE 立方体 / SCOUT 四角錐(高速・蛇行) / HEAVY 八面体(HP3)

  操作:
    矢印 / WASD     視点パン（敵を画面中心へ寄せる）
    左クリック / SPACE  射撃（中心に重なった敵に当たる）
    R              リスタート（ゲームオーバー後）
    ESC            終了

  依存: pygame   実行: python3 wireframe_fps3.py
"""

import os
import sys
import math
import random
import pygame

# ============ 設定 ============
W, H = 900, 560
CX, CY = W / 2, H / 2
F = 520.0
FPS = 60

START_LIVES = 5
FIRE_CD = 0.16
NEAR_Z = 1.2
FORWARD = 7.0              # 星の前進感

PAN_SPEED = 430.0          # 視点パン速度(px/秒)
PAN_X_MAX = 460.0          # パンの可動範囲
PAN_Y_MAX = 300.0

CROSS_COLOR = (90, 230, 160)

# ---- 形状 ----
CUBE_V = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
          (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
CUBE_E = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6),
          (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
PYR_V = [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (0, 1.3, 0)]
PYR_E = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 4), (2, 4), (3, 4)]
OCT_V = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
OCT_E = [(0, 2), (2, 1), (1, 3), (3, 0), (0, 4), (4, 1),
         (1, 5), (5, 0), (2, 4), (4, 3), (3, 5), (5, 2)]

# type -> (verts, edges, color, hp, size, (spd_min,spd_max), points, weave)
TYPES = {
    "drone": (CUBE_V, CUBE_E, (90, 220, 130), 1, 1.0, (3.5, 4.5), 100, 0.0),
    "scout": (PYR_V, PYR_E, (120, 220, 255), 1, 0.65, (5.3, 6.5), 150, 2.2),
    "heavy": (OCT_V, OCT_E, (255, 150, 70), 3, 1.5, (2.3, 3.0), 250, 0.0),
}
SPAWN_TABLE = ["drone", "drone", "drone", "scout", "scout", "heavy"]


def project(x, y, z):
    if z <= 0.3:
        return None
    return CX + (x / z) * F, CY - (y / z) * F


def rotate(p, ay, ax):
    x, y, z = p
    cy, sy = math.cos(ay), math.sin(ay)
    x, z = x * cy + z * sy, -x * sy + z * cy
    cx, sx = math.cos(ax), math.sin(ax)
    y, z = y * cx - z * sx, y * sx + z * cx
    return x, y, z


# ============ 敵 ============
class Enemy:
    __slots__ = ("type", "x", "y", "z", "size", "speed", "hp",
                 "spin", "spin_v", "weave", "phase", "hurt")

    def __init__(self, etype):
        v, e, col, hp, size, spd, pts, weave = TYPES[etype]
        self.type = etype
        self.x = random.uniform(-6.5, 6.5)
        self.y = random.uniform(-3.0, 3.2)
        self.z = random.uniform(30.0, 36.0)
        self.size = size
        self.speed = random.uniform(*spd)
        self.hp = hp
        self.spin = random.uniform(0, math.tau)
        self.spin_v = random.uniform(-1.8, 1.8)
        self.weave = weave
        self.phase = random.uniform(0, math.tau)
        self.hurt = 0.0


# ============ ゲーム ============
class Game:
    def __init__(self, headless=False):
        if headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        pygame.init()
        pygame.font.init()
        self.headless = headless
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Wireframe FPS 3")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22, bold=True)
        self.big = pygame.font.SysFont("monospace", 56, bold=True)
        self.reset()

    def reset(self):
        self.enemies = []
        self.score = 0
        self.lives = START_LIVES
        self.spawn_t = 0.4
        self.fire_cd = 0.0
        self.pan = [0.0, 0.0]      # 画面全体のパン量
        self.flash = 0.0
        self.shots = []
        self.state = "play"
        self.stars = [[random.uniform(-14, 14),
                       random.uniform(-9, 9),
                       random.uniform(2, 42)] for _ in range(140)]

    @property
    def spawn_interval(self):
        return max(0.72, 1.45 - self.score * 0.0005)

    # ---------- 入力 ----------
    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return False
                if e.key == pygame.K_r and self.state == "over":
                    self.reset()
                if e.key == pygame.K_SPACE and self.state == "play":
                    self.fire()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.state == "play":
                self.fire()
        return True

    def update_pan(self, dt):
        """移動キーで画面全体を逆方向へ動かす"""
        keys = pygame.key.get_pressed()
        v = PAN_SPEED * dt
        # 右入力→画面は左へ / 上入力→画面は下へ（＝逆方向）
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.pan[0] -= v
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.pan[0] += v
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.pan[1] += v
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.pan[1] -= v
        self.pan[0] = max(-PAN_X_MAX, min(PAN_X_MAX, self.pan[0]))
        self.pan[1] = max(-PAN_Y_MAX, min(PAN_Y_MAX, self.pan[1]))

    # ---------- 射撃 ----------
    def fire(self):
        if self.fire_cd > 0:
            return
        self.fire_cd = FIRE_CD
        self.flash = 0.05
        ox, oy = self.pan
        target = None
        best = 1e30
        for en in self.enemies:
            pr = project(en.x, en.y, en.z)
            if pr is None:
                continue
            sx, sy = pr[0] + ox, pr[1] + oy
            radius = max(18.0, (en.size / en.z) * F * 1.7)
            # 敵の画面座標が中心(自分)と一致しているか
            if math.hypot(sx - CX, sy - CY) <= radius and en.z < best:
                best = en.z
                target = en
        if target is not None:
            target.hp -= 1
            target.hurt = 0.12
            self.shots.append([CX, CY, 0.12])
            if target.hp <= 0:
                self.enemies.remove(target)
                self.score += TYPES[target.type][6]

    # ---------- 更新 ----------
    def update(self, dt):
        if self.fire_cd > 0:
            self.fire_cd -= dt
        if self.flash > 0:
            self.flash -= dt
        for s in self.shots:
            s[2] -= dt
        self.shots = [s for s in self.shots if s[2] > 0]

        # 星は常に流す
        for st in self.stars:
            st[2] -= FORWARD * 2.0 * dt
            if st[2] <= 0.5:
                st[0] = random.uniform(-14, 14)
                st[1] = random.uniform(-9, 9)
                st[2] = random.uniform(38, 44)

        if self.state != "play":
            return

        self.update_pan(dt)

        self.spawn_t -= dt
        if self.spawn_t <= 0:
            self.enemies.append(Enemy(random.choice(SPAWN_TABLE)))
            self.spawn_t = self.spawn_interval

        survivors = []
        for en in self.enemies:
            en.z -= en.speed * dt
            en.spin += en.spin_v * dt
            if en.hurt > 0:
                en.hurt -= dt
            if en.weave:
                en.phase += 2.2 * dt
                en.x += math.cos(en.phase) * en.weave * dt
            if en.z <= NEAR_Z:
                self.lives -= 1
            else:
                survivors.append(en)
        self.enemies = survivors

        if self.lives <= 0:
            self.lives = 0
            self.state = "over"

    # ---------- 描画 ----------
    def line(self, a, b, color, width=1):
        if a and b:
            pygame.draw.line(self.screen, color, a, b, width)

    def draw_stars(self):
        ox, oy = self.pan
        for sx, sy, sz in self.stars:
            head = project(sx, sy, sz)
            if head is None:
                continue
            x, y = int(head[0] + ox), int(head[1] + oy)
            t = max(0.0, min(1.0, (42.0 - sz) / 42.0))
            g = int(120 + 135 * t)
            col = (g, g, min(255, g + 20))
            r = 2 if t > 0.6 else 1            # 近いほど少し大きい点
            pygame.draw.circle(self.screen, col, (x, y), r)

    def draw_enemy(self, en):
        v, e, col, _, _, _, _, _ = TYPES[en.type]
        ox, oy = self.pan
        pts = []
        for vert in v:
            rx, ry, rz = rotate(vert, en.spin, en.spin * 0.6)
            p = project(en.x + rx * en.size, en.y + ry * en.size, en.z + rz * en.size)
            pts.append((p[0] + ox, p[1] + oy) if p else None)
        t = max(0.0, min(1.0, (36.0 - en.z) / 34.0))
        if en.hurt > 0:
            color = (255, 255, 255)
        else:
            color = (int(col[0] * (0.45 + 0.55 * t)),
                     int(col[1] * (0.45 + 0.55 * t)),
                     int(col[2] * (0.45 + 0.55 * t)))
        for a, b in e:
            self.line(pts[a], pts[b], color, 2)

    def draw_cross(self):
        # 照準は画面中心に固定（パンの影響を受けない）
        x, y = int(CX), int(CY)
        r = 16
        pygame.draw.circle(self.screen, CROSS_COLOR, (x, y), r, 2)
        self.line((x - r - 6, y), (x - 4, y), CROSS_COLOR, 2)
        self.line((x + 4, y), (x + r + 6, y), CROSS_COLOR, 2)
        self.line((x, y - r - 6), (x, y - 4), CROSS_COLOR, 2)
        self.line((x, y + 4), (x, y + r + 6), CROSS_COLOR, 2)

    def draw_shots(self):
        for sx, sy, t in self.shots:
            r = int(6 + (0.12 - t) * 220)
            pygame.draw.circle(self.screen, (255, 220, 120), (int(sx), int(sy)), r, 2)

    def draw_hud(self):
        self.screen.blit(self.font.render(f"SCORE {self.score}", True, (230, 230, 230)),
                         (16, 12))
        label = self.font.render("LIVES", True, (230, 230, 230))
        spacing, box = 22, 16
        block_w = label.get_width() + 12 + START_LIVES * spacing
        x0 = W - 16 - block_w
        self.screen.blit(label, (x0, 12))
        ix = x0 + label.get_width() + 12
        for i in range(START_LIVES):
            rect = (ix + i * spacing, 14, box, box)
            if i < self.lives:
                pygame.draw.rect(self.screen, (90, 230, 160), rect)
            else:
                pygame.draw.rect(self.screen, (70, 80, 80), rect, 1)
        if self.flash > 0:
            self.screen.fill((26, 34, 26), special_flags=pygame.BLEND_RGB_ADD)

    def draw_over(self):
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        self.screen.blit(ov, (0, 0))
        t = self.big.render("GAME OVER", True, (230, 90, 90))
        self.screen.blit(t, (CX - t.get_width() / 2, CY - 70))
        s = self.font.render(f"SCORE {self.score}   -   press R to restart",
                             True, (230, 230, 230))
        self.screen.blit(s, (CX - s.get_width() / 2, CY + 8))

    def draw(self):
        self.screen.fill((6, 8, 14))
        self.draw_stars()
        for en in sorted(self.enemies, key=lambda e: -e.z):
            self.draw_enemy(en)
        self.draw_shots()
        self.draw_cross()
        self.draw_hud()
        if self.state == "over":
            self.draw_over()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            running = self.events()
            self.update(dt)
            self.draw()
        pygame.quit()


# ============ セルフテスト ============
def selftest(frames=600):
    g = Game(headless=True)
    seen = set()
    for n in range(frames):
        dt = 1.0 / FPS
        # 最も近い敵を中心へ寄せる（パンを直接合わせる）ように撃つ
        if g.enemies and n % 5 == 0:
            tgt = min(g.enemies, key=lambda e: e.z)
            pr = project(tgt.x, tgt.y, tgt.z)
            if pr:
                g.pan[0] = CX - pr[0]
                g.pan[1] = CY - pr[1]
            g.fire_cd = 0.0
            g.fire()
        for e in g.enemies:
            seen.add(e.type)
        g.update(dt)
        g.draw()
    print(f"[selftest] OK frames={frames} state={g.state} score={g.score} "
          f"lives={g.lives} enemies={len(g.enemies)} types_seen={sorted(seen)} "
          f"pan=({g.pan[0]:.0f},{g.pan[1]:.0f})")
    pygame.quit()


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        Game().run()

```
