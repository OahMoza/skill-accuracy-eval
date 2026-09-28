#!/usr/bin/env node
'use strict';
/*
 * skill-accuracy-eval 安装脚本（通用智能体版）
 * 支持安装到豆包 / Claude Code / OpenCode / Cursor / Codex / Windsurf / 自定义目录。
 *
 * 用法：
 *   npx github:OahMoza/skill-accuracy-eval                 # 交互式选择平台（TTY）
 *   npx github:OahMoza/skill-accuracy-eval --platform claude   # 直接指定平台
 *   npx github:OahMoza/skill-accuracy-eval --dir <路径>        # 自定义目录
 *   npx github:OahMoza/skill-accuracy-eval --list              # 列出平台与默认目录
 *   npx github:OahMoza/skill-accuracy-eval --yes               # 非交互：装到检测到的平台（无则豆包默认）
 */
const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');

const SRC = __dirname;
const NAME = 'skill-accuracy-eval';
const ITEMS = ['SKILL.md', 'references', 'assets'];

const PLATFORMS = [
  { id: 'doubao',   name: '豆包',        dir: () => path.join(os.homedir(), '.doubao', 'skills') },
  { id: 'claude',   name: 'Claude Code', dir: () => path.join(os.homedir(), '.claude', 'skills') },
  { id: 'opencode', name: 'OpenCode',    dir: () => path.join(os.homedir(), '.config', 'opencode', 'skills') },
  { id: 'cursor',   name: 'Cursor',      dir: () => path.join(os.homedir(), '.cursor', 'skills') },
  { id: 'codex',    name: 'Codex',       dir: () => path.join(os.homedir(), '.agents', 'skills') },
  { id: 'windsurf', name: 'Windsurf',    dir: () => path.join(os.homedir(), '.windsurf', 'skills') },
];

function parseArgs(argv) {
  const out = { platform: null, dir: null, yes: false, list: false, help: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--platform' && argv[i + 1]) { out.platform = argv[i + 1].toLowerCase(); i++; }
    else if (argv[i] === '--dir' && argv[i + 1]) { out.dir = argv[i + 1]; i++; }
    else if (argv[i] === '--yes') out.yes = true;
    else if (argv[i] === '--list') out.list = true;
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
  if (fs.statSync(src).isDirectory()) copyDir(src, dest);
  else { fs.mkdirSync(path.dirname(dest), { recursive: true }); fs.copyFileSync(src, dest); }
}

function installTo(base) {
  const dest = path.join(base, NAME);
  console.log('skill-accuracy-eval 安装到: ' + dest);
  for (const item of ITEMS) {
    const s = path.join(SRC, item);
    if (!fs.existsSync(s)) { console.error('错误: 技能包缺少文件 ' + item); process.exit(1); }
    copyItem(s, path.join(dest, item));
  }
  console.log('安装完成。');
  console.log('用法：向支持技能的 agent 提问"评测某技能的准确性"并触发 skill-accuracy-eval，或直接按 SKILL.md 指引操作。');
}

function platformDir(id) {
  const p = PLATFORMS.find(x => x.id === id);
  return p ? p.dir() : null;
}

function detectExisting() {
  return PLATFORMS.filter(p => fs.existsSync(p.dir()));
}

function promptChoice(rl, question) {
  return new Promise(resolve => rl.question(question, resolve));
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    console.log('用法: npx github:OahMoza/skill-accuracy-eval [选项]');
    console.log('  --platform <id>   指定平台: ' + PLATFORMS.map(p => p.id).join(' / '));
    console.log('  --dir <路径>       自定义安装目录（优先级最高）');
    console.log('  --yes              非交互：自动选择检测到的平台，无则豆包默认');
    console.log('  --list             列出平台与默认目录');
    process.exit(0);
  }

  if (args.list) {
    console.log('支持的平台与默认技能目录：');
    for (const p of PLATFORMS) {
      const d = p.dir();
      console.log('  ' + p.id.padEnd(9) + p.name.padEnd(12) + ' -> ' + d + (fs.existsSync(d) ? '  [已存在]' : ''));
    }
    console.log('自定义: --dir <路径>');
    process.exit(0);
  }

  // 1) --dir 优先级最高
  if (args.dir) { installTo(args.dir); return; }

  // 2) --platform 直接指定
  if (args.platform) {
    const dir = platformDir(args.platform);
    if (!dir) { console.error('未知平台: ' + args.platform + '（可用: ' + PLATFORMS.map(p => p.id).join(' / ') + '）'); process.exit(1); }
    installTo(dir);
    return;
  }

  // 3) 交互式选择（TTY 且未 --yes）
  const isTTY = Boolean(process.stdin.isTTY);
  if (!args.yes && isTTY) {
    console.log('skill-accuracy-eval 安装目标选择：');
    const existing = detectExisting();
    PLATFORMS.forEach((p, i) => {
      const mark = existing.includes(p) ? '  [检测到]' : '';
      console.log('  ' + (i + 1) + '. ' + p.id.padEnd(9) + p.name.padEnd(12) + ' -> ' + p.dir() + mark);
    });
    console.log('  ' + (PLATFORMS.length + 1) + '. 自定义路径');
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    const ans = (await promptChoice(rl, '请选择序号（默认 1. 豆包）：')).trim();
    rl.close();
    const n = parseInt(ans, 10);
    if (ans && Number.isInteger(n) && n >= 1 && n <= PLATFORMS.length) { installTo(PLATFORMS[n - 1].dir()); return; }
    if (ans && Number.isInteger(n) && n === PLATFORMS.length + 1) {
      const rl2 = readline.createInterface({ input: process.stdin, output: process.stdout });
      const custom = (await promptChoice(rl2, '请输入自定义目录：')).trim();
      rl2.close();
      if (!custom) { console.log('已取消，未安装。'); process.exit(0); }
      installTo(custom); return;
    }
    installTo(PLATFORMS[0].dir()); return;
  }

  // 4) 非交互：检测已存在的平台目录，否则豆包默认
  const existing = detectExisting();
  if (existing.length > 0) { installTo(existing[0].dir()); return; }
  installTo(PLATFORMS[0].dir());
}

main().catch(e => { console.error(e.message); process.exit(1); });
