---
id: "2026-07-15-sanook-ai-claude-code-21208-ไมไดทำใหโมเดลเขยนโคดเก-01"
title: "@sanook_ai: Claude Code 2.1.208 ไม่ได้ทำให้โมเดลเขียนโค้ดเก่งขึ้นครับ แต"
url: "https://x.com/sanook_ai/status/2077256848474767424"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "x"]
date_published: "2026-07-15"
date_collected: "2026-07-15"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Claude Code 2.1.208 ไม่ได้ทำให้โมเดลเขียนโค้ดเก่งขึ้นครับ แต่มันแก้หลายเรื่องที่ทำให้คนใช้ CLI หงุดหงิดทุกวัน
.
Anthropic ใส่การเปลี่ยนแปลงมา 45 รายการ ส่วนใหญ่เน้น accessibility, background agents, automation และการลดการใช้ memory/CPU
.
ผมเลือก 3 เรื่องที่กระทบงานจริงที่สุดมาเล่า
.
1. เพิ่ม Screen Reader Mode
.
Claude Code มีโหมดแสดงผลแบบ plain text สำหรับผู้ใช้ screen reader แล้ว เปิดได้ด้วย `claude --ax-screen-reader` หรือตั้งค่า `axScreenReader: true`
.
เรื่องนี้ไม่ใช่แค่ปรับหน้าตา แต่ช่วยให้เครื่องมืออ่านหน้าจอตามลำดับข้อมูลใน terminal ได้ง่ายขึ้น
.
2. ข้อความตอบ Background Agent ไม่หายแล้ว
.
ก่อนหน้านี้ถ้าเราพิมพ์ตอบ agent ที่ทำงานเบื้องหลัง แล้วการส่งล้มเหลว ข้อความนั้นอาจหายไปเลย
.
รอบนี้ระบบจะบันทึกข้อความไว้ และส่งให้อีกครั้งเมื่อ session กลับมาทำงาน
.
ต้องระบุให้ตรงว่าไม่ได้บันทึก “ทุกข้อความร่าง” นะครับ แต่บันทึกเฉพาะข้อความที่พยายามส่งให้ background agent แล้วส่งไม่สำเร็จ
.
3. `claude -p` ส่งผลลัพธ์ใหญ่ได้ครบขึ้น
.
Claude Code แก้ปัญหา JSON และ stream-json ถูกตัดเมื่อ pipe คำตอบขนาดใหญ่ ทำให้ workflow ที่เรียกผ่าน CI, script หรือ Agent SDK มีโอกาสได้รับ result message ครบ ไม่จบกลางไฟล์แบบเงียบ ๆ
.
ของดีที่ซ่อนอยู่ยังมีอีก เช่น ลด memory leak ใน session ยาว, จำกัดตาราง Markdown เกิน 200 แถว, ทำให้ permission rules จำนวนมากประมวลผลเร็วขึ้น และลดภาระจาก MCP tools
.
Anthropic ระบุว่า tool rounds บางกรณีที่มี MCP จำนวนมากอาจเร็วขึ้นสูงสุด 7 เท่า และ transcript ของงานแก้ไฟล์หนัก ๆ อาจเล็กลงสูงสุด 79 เท่า
.
แต่ตัวเลขนี้เป็นกรณีเฉพาะจาก changelog ไม่ใช่ความเร็วที่ทุกเครื่องจะได้รับเท่ากัน และรุ่นนี้ไม่ได้เปลี่ยนโมเดลหรือรับประกันว่าโค้ดจะถูกต้องขึ้น
.
ผมตรวจจาก Changelog ทางการ, GitHub และ npm แล้วครับ 2.1.208 มี 45 รายการจริง แต่ตอนเช็ก Anthropic ออก 2.1.209 ตามมาแล้ว เพื่อแก้ dialog อย่าง `/model` ที่ถูกบล็อกใน background session
.
เช็กด้วย `claude --version` และอัปเดตด้วย `claude update` ได้ครับ ทั้งนี้เวอร์ชันที่ได้รับอาจขึ้นอยู่กับ release channel
.
ในมุมผม รอบนี้ไม่ใช่อัปเดตเอาไว้โชว์ แต่มันทำให้ Claude Code ไว้ใจได้ขึ้นเวลาเอาไปต่อกับงานจริง ซึ่งสำคัญกว่
