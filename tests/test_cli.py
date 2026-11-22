"""cli 模块的单元测试。"""
from __future__ import annotations

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from typing import Dict, Sequence, Tuple
from unittest import mock

from animalclassification import __version__, cli


class _RecordingStream:
    """记录 reconfigure 参数的假输出流。"""

    def __init__(self) -> None:
        self.kwargs: Dict[str, object] = {}

    def reconfigure(self, **kwargs: object) -> None:
        self.kwargs = kwargs


class _ValueErrorStream:
    """reconfigure 抛出 ValueError 的假输出流。"""

    def reconfigure(self, **kwargs: object) -> None:
        raise ValueError("流已关闭")


class _OSErrorStream:
    """reconfigure 抛出 OSError 的假输出流。"""

    def reconfigure(self, **kwargs: object) -> None:
        raise OSError("无法配置")


class CliTests(unittest.TestCase):
    """命令行入口与子命令测试。"""

    def _run(self, argv: Sequence[str]) -> Tuple[int, str, str]:
        """捕获标准输出/错误后执行 main。"""
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_info_animal(self) -> None:
        code, out, err = self._run(["info", "鲸"])
        self.assertEqual(code, 0)
        self.assertIn("名称：鲸", out)
        self.assertIn("类别：哺乳类（脊椎动物）", out)
        self.assertIn("食性：肉食", out)
        self.assertIn("别名：鲸鱼", out)
        self.assertEqual(err, "")

    def test_info_alias(self) -> None:
        code, out, _ = self._run(["info", "大熊猫"])
        self.assertEqual(code, 0)
        self.assertIn("名称：熊猫", out)

    def test_info_unknown(self) -> None:
        code, _, err = self._run(["info", "恐龙"])
        self.assertEqual(code, 2)
        self.assertIn("错误：", err)
        self.assertIn("未找到动物", err)

    def test_list_category(self) -> None:
        code, out, _ = self._run(["list", "鸟类"])
        self.assertEqual(code, 0)
        self.assertIn("类别：鸟类（9 种）", out)
        self.assertIn("猫头鹰", out)
        self.assertIn("肉食", out)

    def test_list_alias(self) -> None:
        code, out, _ = self._run(["list", "兽类"])
        self.assertEqual(code, 0)
        self.assertIn("类别：哺乳类", out)

    def test_list_unknown(self) -> None:
        code, _, err = self._run(["list", "恐龙类"])
        self.assertEqual(code, 2)
        self.assertIn("未知类别", err)

    def test_list_empty(self) -> None:
        code, _, err = self._run(["list", ""])
        self.assertEqual(code, 2)
        self.assertIn("不能为空", err)

    def test_categories(self) -> None:
        code, out, _ = self._run(["categories"])
        self.assertEqual(code, 0)
        self.assertIn("11 个类别，87 种动物", out)
        self.assertIn("脊椎动物", out)
        self.assertIn("无脊椎动物", out)
        self.assertIn("棘皮类", out)

    def test_diet(self) -> None:
        code, out, _ = self._run(["diet", "鲸"])
        self.assertEqual(code, 0)
        self.assertIn("鲸是肉食动物。", out)

    def test_diet_alias(self) -> None:
        code, out, _ = self._run(["diet", "娃娃鱼"])
        self.assertEqual(code, 0)
        self.assertIn("大鲵是肉食动物。", out)

    def test_diet_unknown(self) -> None:
        code, _, err = self._run(["diet", "恐龙"])
        self.assertEqual(code, 2)
        self.assertIn("未找到动物", err)

    def test_quiz_console(self) -> None:
        code, out, _ = self._run(["quiz", "--count", "3", "--seed", "5"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count("解析："), 3)
        self.assertIn("答案：", out)

    def test_quiz_group(self) -> None:
        code, out, _ = self._run(
            ["quiz", "--count", "5", "--seed", "1", "--group", "脊椎"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(out.count("解析："), 5)

    def test_quiz_invalid_group(self) -> None:
        code, _, err = self._run(["quiz", "--count", "3", "--group", "海洋"])
        self.assertEqual(code, 2)
        self.assertIn("脊椎", err)

    def test_quiz_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = os.path.join(temp, "quiz.html")
            code, out, _ = self._run(
                ["quiz", "--count", "4", "--seed", "2", "-o", path]
            )
            self.assertEqual(code, 0)
            self.assertIn("已生成：%s" % path, out)
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("共 4 道单选题", content)
            self.assertNotIn("解析：", content)

    def test_quiz_invalid_count(self) -> None:
        code, _, err = self._run(["quiz", "--count", "0"])
        self.assertEqual(code, 2)
        self.assertIn("1 到 40", err)

    def test_match_console(self) -> None:
        code, out, _ = self._run(["match", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("共 3 组", out)
        self.assertIn("——", out)

    def test_match_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = os.path.join(temp, "match.html")
            code, out, _ = self._run(
                ["match", "--count", "5", "--seed", "3", "-o", path]
            )
            self.assertEqual(code, 0)
            self.assertIn("已生成：%s" % path, out)
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("match-columns", content)
            self.assertIn("共 5 组配对", content)

    def test_match_invalid_count(self) -> None:
        code, _, err = self._run(["match", "--count", "21"])
        self.assertEqual(code, 2)
        self.assertIn("1 到 20", err)

    def test_poster_stdout(self) -> None:
        code, out, _ = self._run(["poster"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)
        self.assertIn("动物分类海报", out)
        self.assertIn("分类树", out)

    def test_poster_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = os.path.join(temp, "poster.html")
            code, out, _ = self._run(["poster", "-o", path])
            self.assertEqual(code, 0)
            self.assertIn("已生成：%s" % path, out)
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("动物分类海报", content)
            self.assertIn("鱼类", content)

    def test_poster_bad_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            code, _, err = self._run(["poster", "-o", temp])
            self.assertEqual(code, 2)
            self.assertIn("无法写入文件", err)

    def test_poster_empty_output(self) -> None:
        code, _, err = self._run(["poster", "-o", ""])
        self.assertEqual(code, 2)
        self.assertIn("输出路径不能为空", err)

    def test_help(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            with self.assertRaises(SystemExit) as ctx:
                cli.main(["--help"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("动物分类", out.getvalue())

    def test_version(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            with self.assertRaises(SystemExit) as ctx:
                cli.main(["--version"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn(__version__, out.getvalue())

    def test_unknown_command(self) -> None:
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                cli.main(["unknown"])
        self.assertEqual(ctx.exception.code, 2)

    def test_no_command(self) -> None:
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                cli.main([])
        self.assertEqual(ctx.exception.code, 2)


class WriteTextTests(unittest.TestCase):
    """_write_text 测试。"""

    def test_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = os.path.join(temp, "nested", "file.html")
            cli._write_text(path, "内容")
            with open(path, encoding="utf-8") as handle:
                self.assertEqual(handle.read(), "内容")

    def test_rejects_non_string_path(self) -> None:
        with self.assertRaises(TypeError):
            cli._write_text(123, "内容")  # type: ignore[arg-type]

    def test_rejects_empty_path(self) -> None:
        with self.assertRaises(ValueError):
            cli._write_text("   ", "内容")

    def test_rejects_non_string_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = os.path.join(temp, "file.html")
            with self.assertRaises(TypeError):
                cli._write_text(path, 123)  # type: ignore[arg-type]


class Utf8ConsoleTests(unittest.TestCase):
    """_ensure_utf8_console 测试。"""

    def test_records_utf8_settings(self) -> None:
        out = _RecordingStream()
        err = _RecordingStream()
        with mock.patch.object(cli.sys, "stdout", out), mock.patch.object(
            cli.sys, "stderr", err
        ):
            cli._ensure_utf8_console()
        self.assertEqual(out.kwargs.get("encoding"), "utf-8")
        self.assertEqual(out.kwargs.get("errors"), "replace")
        self.assertEqual(err.kwargs.get("encoding"), "utf-8")
        self.assertEqual(err.kwargs.get("errors"), "replace")

    def test_catches_value_error(self) -> None:
        with mock.patch.object(cli.sys, "stdout", _ValueErrorStream()), mock.patch.object(
            cli.sys, "stderr", _ValueErrorStream()
        ):
            cli._ensure_utf8_console()

    def test_catches_os_error(self) -> None:
        with mock.patch.object(cli.sys, "stdout", _OSErrorStream()), mock.patch.object(
            cli.sys, "stderr", _OSErrorStream()
        ):
            cli._ensure_utf8_console()

    def test_skips_stream_without_reconfigure(self) -> None:
        with mock.patch.object(cli.sys, "stdout", object()), mock.patch.object(
            cli.sys, "stderr", object()
        ):
            cli._ensure_utf8_console()


if __name__ == "__main__":
    unittest.main()
