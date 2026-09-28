#!/usr/bin/env node
'use strict';
/*
 * skill-accuracy-eval 安装脚本
 * 由 npx github:OahMoza/skill-accuracy-eval 触发：把技能包（SKILL.md + references + assets）复制到目标技能根目录。
 * 默认目标： ~/.doubao/skills/skill-accuracy-eval
 * 自定义：    npx github:OahMoza/skill-accuracy-eval --dir <技能根目录>
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

const SRC = __dirname;
const NAME = 'skill-accuracy-eval';
const ITEMS = ['SKILL.md', 'references', 'assets'];

function parseArgs(argv) {
  const out = { dir: null, help: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--dir' && argv[i + 1]) { out.dir = argv[i + 1]; i++; }
    else if (argv[i] === '--help' || argv[i] === '-h') out.help = true;
  }
  return out;
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}

function copyItem(src, dest) {
  if (fs.statSync(src).isDirectory()) {
    copyDir(src, dest);
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
  }
}

const args = parseArgs(process.argv.slice(2));
if (args.help) {
  console.log('用法: npx github:OahMoza/skill-accuracy-eval [--dir <技能根目录>]');
  console.log('默认安装到 ~/.doubao/skills/skill-accuracy-eval');
  process.exit(0);
}

const base = args.dir || path.join(os.homedir(), '.doubao', 'skills');
const dest = path.join(base, NAME);

console.log('skill-accuracy-eval 安装到: ' + dest);

for (const item of ITEMS) {
  const s = path.join(SRC, item);
  if (!fs.existsSync(s)) {
    console.error('错误: 技能包缺少文件 ' + item);
    process.exit(1);
  }
  copyItem(s, path.join(dest, item));
}

console.log('安装完成。');
console.log('使用：向支持技能的 agent 提问"评测某技能的准确性"并触发 skill-accuracy-eval，或直接按 SKILL.md 指引操作。');
console.log('提示：若你的豆包技能根目录不是 ~/.doubao/skills，请用 --dir 指定，例如：');
console.log('  npx github:OahMoza/skill-accuracy-eval --dir "C:\\Users\\<you>\\AppData\\Local\\Doubao\\User Data\\<profile>\\.doubao\\agent_mode\\workspace\\.user_skills"');
