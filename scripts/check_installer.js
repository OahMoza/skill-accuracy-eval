#!/usr/bin/env node
/**
 * 安装器边界回归（Node vm + 假 fs，只记录调用，不真实写入）。
 * 被 scripts/check_regression.py 调用：node check_installer.js <install.js 路径>。
 * 退出码：0 = 全部通过；1 = 有失败；2 = 用法错误。
 */
'use strict';
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const target = process.argv[2];
if (!target) {
  console.error('usage: node check_installer.js <install.js path>');
  process.exit(2);
}
const code = fs.readFileSync(target, 'utf8');

const groups = [
  { args: ['--dir'], expect: 'help' },          // 缺参
  { args: ['--dir', ''], expect: 'help' },      // 空串
  { args: ['--dir', '   '], expect: 'help' },   // 全空白
  { args: ['--dir', '--bogus'], expect: 'help' }, // flag 伪值
  { args: ['--dir', '.'], expect: 'copy' },     // 合法相对路径 → 进入复制分支
];

let failed = 0;
for (const g of groups) {
  const events = [];
  const fake = {
    mkdirSync: p => events.push(['mkdir', p]),
    readdirSync: () => [],
    statSync: () => ({ isDirectory: () => false }),
    existsSync: () => true,
    copyFileSync: (s, d) => events.push(['copy', s, d]),
  };
  let exit = null;
  try {
    vm.runInNewContext(code, {
      require: n => (n === 'fs' ? fake : path),
      __dirname: process.cwd(),
      process: { argv: ['node', 'install.js', ...g.args], exit: c => { throw { exit: c }; } },
      console: { log: () => {}, error: () => {} },
    });
  } catch (e) { exit = e.exit !== undefined ? e.exit : String(e); }
  const isHelp = exit === 0 && events.length === 0;
  const isCopy = exit === null && events.length > 0;
  const ok = (g.expect === 'help' && isHelp) || (g.expect === 'copy' && isCopy);
  console.log((ok ? 'PASS' : 'FAIL') + ' installer ' + JSON.stringify(g.args) +
    ' -> exit=' + exit + ' events=' + events.length + ' expect=' + g.expect);
  if (!ok) failed++;
}
process.exit(failed ? 1 : 0);
