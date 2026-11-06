#!/usr/bin/env python3
"""workbuddy_checkin.py 凭据文件权限回归测试（A40）。

背景：auths/<uid>.json 里存的是 accessToken / refreshToken，属于长期有效的
凭据。原先用普通 open() 写盘，POSIX 下是 0644（同机其他用户可读），
Windows 下继承父目录 ACL（通常含 BUILTIN\\Users 可读）。修复后：

  · POSIX：0600（仅属主可读写）
  · Windows：去掉 ACL 继承，只留当前用户 / SYSTEM / Administrators

用法（仓库根目录执行）：
    python -m pytest workbuddy-growth-tasks/tests/test_credential_perms.py -q
或：
    python workbuddy-growth-tasks/tests/test_credential_perms.py
"""
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_DIR = os.path.join(REPO_ROOT, "workbuddy-checkin-ql")
sys.path.insert(0, SCRIPT_DIR)

import workbuddy_checkin as W  # noqa: E402


def assert_not_world_readable(case, path):
    """断言文件对同机其他用户不可读。

    Windows：不得残留继承项（icacls 输出里的 ``(I)`` 标记），也不得出现
    BUILTIN\\Users / Authenticated Users / Everyone 这类其他用户主体。
    POSIX：组/其他权限位必须为 0。
    """
    case.assertTrue(os.path.isfile(path), "文件未生成: %s" % path)
    if os.name == "nt":
        out = subprocess.run(["icacls", path], capture_output=True)
        text = out.stdout.decode("mbcs", "replace")
        case.assertNotIn("(I)", text,
                         "ACL 仍是继承项（未去掉继承）:\n%s" % text)
        for bad in ("BUILTIN\\Users", "Authenticated Users", "Everyone"):
            case.assertNotIn(bad, text,
                             "ACL 仍对其他用户开放 (%s):\n%s" % (bad, text))
    else:
        mode = stat.S_IMODE(os.stat(path).st_mode)
        case.assertEqual(mode & 0o077, 0,
                         "权限位应收紧为 0600，实际 %o" % mode)


class TestCredentialFilePermissions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="wb-cred-test-")
        self.addCleanup(self._cleanup)
        self._old_auth_dir = W.AUTH_DIR
        W.AUTH_DIR = os.path.join(self.tmp, "auths")
        self.addCleanup(self._restore_auth_dir)

    def _restore_auth_dir(self):
        W.AUTH_DIR = self._old_auth_dir

    def _cleanup(self):
        for root, dirs, files in os.walk(self.tmp, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except OSError:
                    pass
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except OSError:
                    pass
        try:
            os.rmdir(self.tmp)
        except OSError:
            pass

    def test_save_session_credential_not_world_readable(self):
        session = {
            "account": {"uid": "u-1", "nickname": "n"},
            "auth": {"accessToken": "at-secret", "refreshToken": "rt-secret"},
        }
        self.assertTrue(W.save_session("u-1", session))
        path = os.path.join(W.AUTH_DIR, "u-1.json")
        assert_not_world_readable(self, path)

    def test_save_session_content_unchanged(self):
        session = {
            "account": {"uid": "u-2", "nickname": "n"},
            "auth": {"accessToken": "at-secret", "refreshToken": "rt-secret"},
        }
        W.save_session("u-2", session)
        path = os.path.join(W.AUTH_DIR, "u-2.json")
        with open(path, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["auth"]["refreshToken"], "rt-secret")

    def test_auth_dir_not_world_readable(self):
        """凭据目录本身也不能对其他用户开放（Windows 下文件 ACL 依赖目录）。"""
        session = {"account": {"uid": "u-3"}, "auth": {"accessToken": "a"}}
        W.save_session("u-3", session)
        if os.name != "nt":
            mode = stat.S_IMODE(os.stat(W.AUTH_DIR).st_mode)
            self.assertEqual(mode & 0o077, 0,
                             "auths 目录权限位应收紧为 0700，实际 %o" % mode)
        else:
            out = subprocess.run(["icacls", W.AUTH_DIR], capture_output=True)
            text = out.stdout.decode("mbcs", "replace")
            self.assertNotIn("(I)", text,
                             "auths 目录 ACL 仍是继承项:\n%s" % text)
            for bad in ("BUILTIN\\Users", "Authenticated Users", "Everyone"):
                self.assertNotIn(bad, text,
                                 "auths 目录 ACL 仍对其他用户开放 (%s):\n%s" % (bad, text))

    def test_no_tmp_leftover(self):
        session = {"account": {"uid": "u-4"}, "auth": {"accessToken": "a"}}
        W.save_session("u-4", session)
        self.assertFalse(os.path.exists(os.path.join(W.AUTH_DIR, "u-4.json.tmp")))

    def test_do_login_writes_restricted_credential(self):
        """login 流程写盘同样必须收紧权限（它不走 save_session）。"""
        src = os.path.join(self.tmp, "desktop.info")
        session = {
            "account": {"uid": "u-5", "nickname": "n"},
            "auth": {"accessToken": "at-secret", "refreshToken": "rt-secret"},
        }
        with open(src, "w", encoding="utf-8") as f:
            json.dump(session, f)
        old_find = W.find_local_auth_file
        W.find_local_auth_file = lambda: src
        try:
            self.assertEqual(W.do_login(), 0)
        finally:
            W.find_local_auth_file = old_find
        path = os.path.join(W.AUTH_DIR, "u-5.json")
        assert_not_world_readable(self, path)
        with open(path, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["auth"]["refreshToken"], "rt-secret")


if __name__ == "__main__":
    unittest.main(verbosity=2)
