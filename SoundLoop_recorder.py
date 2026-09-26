# -*- coding: utf-8 -*-
"""
SoundLoop Recorder · 声环录制器
一键监听并录制电脑扬声器输出的声音（WASAPI loopback，不含麦克风）。
支持录音列表、时间裁剪、导出 MP3，内置中/英文一键切换。

运行: python SoundLoop_recorder.py
"""
import os
import sys
import io
import wave
import threading
import subprocess
import tempfile
import datetime
import warnings
from tkinter import (
    Tk, StringVar, filedialog, messagebox,
    ttk, Label, Button, Entry, Frame, LabelFrame, Listbox, Scrollbar,
    END, ACTIVE, N, S, E, W,
)

# 控制台/文件输出统一 UTF-8（Windows 下避免乱码）
if sys.stdout and hasattr(sys.stdout, "buffer"):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        pass

import numpy as np

try:
    import soundcard as sc
    try:
        from soundcard.mediafoundation import SoundcardRuntimeWarning
        warnings.filterwarnings("ignore", category=SoundcardRuntimeWarning)
    except Exception:
        pass
except Exception:
    sc = None

# ============ 双语文案 ============
L = {
    "zh": {
        "app_title": "声环录制器 · SoundLoop Recorder",
        "status_ready": "就绪",
        "start_rec": "● 开始录制",
        "stop_rec": "■ 停止录制",
        "recording": "正在录制系统声音… {} 秒",
        "saved": "已保存 {}",
        "no_audio": "未录到有效音频",
        "export_mp3": "导出 MP3",
        "rec_list": "录音列表：",
        "play": "▶ 播放",
        "delete": "删除",
        "clear": "清空",
        "cut_frame": "裁剪（可选，剪掉不需要的片段）",
        "start_sec": "开始(秒):",
        "end_sec": "结束(秒):",
        "empty_to_end": "(留空=到末尾)",
        "preview_info": "预览信息",
        "apply_cut": "应用裁剪",
        "duration": "时长: -",
        "duration_fmt": "时长: {:.1f} 秒（{} Hz）",
        "rec_note": "录制的是电脑扬声器输出的声音（不含麦克风）",
        "ffmpeg_found": "ffmpeg: 已找到 ✓",
        "ffmpeg_missing": "ffmpeg: 未找到 ✗（需安装才能导出 MP3）",
        "lang_btn": "English",
        "select_first": "请先在列表中选择一段录音",
        "no_ffmpeg_play": "未找到播放器（需 ffmpeg）",
        "no_ffmpeg_export": "未找到 ffmpeg，无法导出 MP3。\n请安装 ffmpeg 后重试。",
        "invalid_range": "无效范围：结束必须大于开始",
        "cut_preview": "将保留 {:.1f} 秒 ~ {:.1f} 秒（共 {:.1f} 秒），其余被剪掉",
        "cut_applied": "已应用裁剪",
        "exporting": "正在导出 MP3…",
        "export_done": "已导出 MP3:\n{}",
        "export_fail": "导出失败",
        "export_fail_detail": "导出失败:\n{}",
        "export_err": "导出出错: {}",
        "read_fail": "读取失败: {}",
        "soundcard_missing": "soundcard 库未安装，无法录音",
    },
    "en": {
        "app_title": "SoundLoop Recorder · 声环录制器",
        "status_ready": "Ready",
        "start_rec": "● Start Recording",
        "stop_rec": "■ Stop Recording",
        "recording": "Recording system audio… {} s",
        "saved": "Saved {}",
        "no_audio": "No audio captured",
        "export_mp3": "Export MP3",
        "rec_list": "Recordings:",
        "play": "▶ Play",
        "delete": "Delete",
        "clear": "Clear All",
        "cut_frame": "Trim (optional — remove unwanted parts)",
        "start_sec": "Start (s):",
        "end_sec": "End (s):",
        "empty_to_end": "(empty = to end)",
        "preview_info": "Preview",
        "apply_cut": "Apply Trim",
        "duration": "Duration: -",
        "duration_fmt": "Duration: {:.1f} s ({} Hz)",
        "rec_note": "Records the sound your speakers play (microphone is NOT captured)",
        "ffmpeg_found": "ffmpeg: found ✓",
        "ffmpeg_missing": "ffmpeg: not found ✗ (needed to export MP3)",
        "lang_btn": "中文",
        "select_first": "Please select a recording from the list first",
        "no_ffmpeg_play": "No player found (needs ffmpeg)",
        "no_ffmpeg_export": "ffmpeg not found — cannot export MP3.\nPlease install ffmpeg and retry.",
        "invalid_range": "Invalid range: end must be greater than start",
        "cut_preview": "Will keep {:.1f}s ~ {:.1f}s ({:.1f}s total); the rest will be removed",
        "cut_applied": "Trim applied",
        "exporting": "Exporting MP3…",
        "export_done": "MP3 exported:\n{}",
        "export_fail": "Export failed",
        "export_fail_detail": "Export failed:\n{}",
        "export_err": "Export error: {}",
        "read_fail": "Read failed: {}",
        "soundcard_missing": "soundcard library not installed — cannot record",
    },
}

SAMPLE_RATE = 48000
CHANNELS = 2
RECORD_DIR = os.path.join(tempfile.gettempdir(), "SoundLoopRecorder")
os.makedirs(RECORD_DIR, exist_ok=True)

FFMPEG_CANDIDATES = [
    "ffmpeg",
    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
    r"C:\ffmpeg\bin\ffmpeg.exe",
    r"C:\Users\Administrator\ffmpeg\bin\ffmpeg.exe",
]


def find_ffmpeg():
    try:
        import imageio_ffmpeg
        p = imageio_ffmpeg.get_ffmpeg_exe()
        if p and os.path.exists(p):
            return p
    except Exception:
        pass
    for c in FFMPEG_CANDIDATES:
        try:
            if os.path.isabs(c):
                if os.path.exists(c):
                    return c
            else:
                subprocess.run([c, "-version"], capture_output=True, timeout=5)
                return c
        except Exception:
            continue
    return None


class Recorder:
    def __init__(self, on_chunk):
        self.on_chunk = on_chunk
        self._stop = threading.Event()
        self._thread = None
        self.chunks = []

    def start(self):
        self.chunks = []
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        try:
            if sc is None:
                self.on_chunk("error")
                return
            speaker = sc.default_speaker()
            mic = sc.get_microphone(id=str(speaker.name), include_loopback=True)
            while not self._stop.is_set():
                data = mic.record(samplerate=SAMPLE_RATE, numframes=SAMPLE_RATE)
                self.chunks.append(data)
                self.on_chunk(data)
        except Exception:
            self.on_chunk("error")

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
        if self.chunks:
            return np.concatenate(self.chunks, axis=0)
        return None


class App:
    def __init__(self, root):
        self.root = root
        self.lang = "zh"
        self.recorder = None
        self.recording = False
        self.records = []
        self.cur = None
        self._cur_dur = None
        self._cur_fr = None
        self._tl = []          # [(widget, key)] 可翻译的静态文本控件
        self.ffmpeg = find_ffmpeg()
        self._build_ui()
        self.root.title(self.t("app_title"))

    def t(self, key):
        return L[self.lang][key]

    # ---------- 界面 ----------
    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}
        main = Frame(self.root)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # 顶部：状态 + 导出 + 语言切换 + 录制
        top = Frame(main)
        top.pack(fill="x")
        self.status = StringVar(value=self.t("status_ready"))
        Label(top, textvariable=self.status, anchor="w").pack(side="left")

        self.lang_btn = Button(top, text=self.t("lang_btn"), command=self._toggle_lang, width=8)
        self.lang_btn.pack(side="right")

        self.rec_btn = Button(top, command=self.toggle_record, width=16)
        self.rec_btn.pack(side="right", padx=4)
        self.btn_export = Button(top, command=self.export_mp3, width=12)
        self.btn_export.pack(side="right", padx=4)
        self._tl.append((self.btn_export, "export_mp3"))
        self._update_rec_btn()

        # 录音列表
        lb = Label(main, text=self.t("rec_list")); lb.pack(anchor="w", **pad); self._tl.append((lb, "rec_list"))
        list_frame = Frame(main)
        list_frame.pack(fill="both", expand=True)
        self.listbox = Listbox(list_frame)
        scroll = Scrollbar(list_frame, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.listbox.bind("<Double-Button-1>", lambda e: self._play_selected())

        btnrow = Frame(main)
        btnrow.pack(fill="x", **pad)
        b1 = Button(btnrow, command=self._play_selected); b1.pack(side="left"); self._tl.append((b1, "play"))
        b2 = Button(btnrow, command=self._delete_selected); b2.pack(side="left", padx=6); self._tl.append((b2, "delete"))
        b3 = Button(btnrow, command=self._clear_all); b3.pack(side="left"); self._tl.append((b3, "clear"))

        # 裁剪区
        cut = LabelFrame(main)
        cut.pack(fill="x", **pad)
        self._tl.append((cut, "cut_frame"))
        g1 = Frame(cut); g1.pack(fill="x", padx=6, pady=4)
        l1 = Label(g1, text=self.t("start_sec")); l1.pack(side="left"); self._tl.append((l1, "start_sec"))
        self.var_start = StringVar(value="0")
        Entry(g1, textvariable=self.var_start, width=10).pack(side="left", padx=4)
        l2 = Label(g1, text=self.t("end_sec")); l2.pack(side="left"); self._tl.append((l2, "end_sec"))
        self.var_end = StringVar(value="")
        Entry(g1, textvariable=self.var_end, width=10).pack(side="left", padx=4)
        l3 = Label(g1, text=self.t("empty_to_end"), fg="gray"); l3.pack(side="left"); self._tl.append((l3, "empty_to_end"))
        b5 = Button(g1, command=self._cut_preview); b5.pack(side="right"); self._tl.append((b5, "preview_info"))
        b4 = Button(g1, command=self._apply_cut); b4.pack(side="right", padx=6); self._tl.append((b4, "apply_cut"))

        self.dur_label = Label(cut, text=self.t("duration"), anchor="w", fg="gray")
        self.dur_label.pack(fill="x", padx=6, pady=(0, 4))

        # 底部说明
        bottom = Frame(main)
        bottom.pack(fill="x", **pad)
        n1 = Label(bottom, text=self.t("rec_note"), fg="gray"); n1.pack(anchor="w"); self._tl.append((n1, "rec_note"))
        self.ff_label = Label(bottom, fg="gray")
        self.ff_label.pack(anchor="w")
        self._update_ff_label()

    def _update_rec_btn(self):
        if self.recording:
            self.rec_btn.config(text=self.t("stop_rec"), bg="#27ae60", fg="white")
        else:
            self.rec_btn.config(text=self.t("start_rec"), bg="#c0392b", fg="white")

    def _update_ff_label(self):
        key = "ffmpeg_found" if self.ffmpeg else "ffmpeg_missing"
        self.ff_label.config(text=self.t(key))

    def _update_duration_label(self):
        if self._cur_dur is not None:
            self.dur_label.config(text=self.t("duration_fmt").format(self._cur_dur, self._cur_fr))
        else:
            self.dur_label.config(text=self.t("duration"))

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        for w, key in self._tl:
            try:
                w.config(text=self.t(key))
            except Exception:
                pass
        self.lang_btn.config(text=self.t("lang_btn"))
        self._update_rec_btn()
        self._update_ff_label()
        self._update_duration_label()
        if self.recording:
            secs = len(self.recorder.chunks) if self.recorder and self.recorder.chunks else 0
            self.status.set(self.t("recording").format(secs))
        else:
            self.status.set(self.t("status_ready"))
        self.root.title(self.t("app_title"))

    # ---------- 录制 ----------
    def toggle_record(self):
        if not self.recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        if sc is None:
            messagebox.showerror(self.t("app_title"), self.t("soundcard_missing"))
            return
        self.recorder = Recorder(self._on_chunk)
        self.recording = True
        self._update_rec_btn()
        self.status.set(self.t("recording").format(0))
        self.recorder.start()

    def _on_chunk(self, data):
        if isinstance(data, str) and data == "error":
            self.status.set(self.t("no_audio"))
            return
        secs = len(self.recorder.chunks) if self.recorder and self.recorder.chunks else 0
        self.status.set(self.t("recording").format(secs))

    def _stop_recording(self):
        self.recorder.stop()
        audio = self.recorder.chunks
        self.recording = False
        self._update_rec_btn()
        if not audio:
            self.status.set(self.t("no_audio"))
            return
        data = np.concatenate(audio, axis=0)
        if data.ndim > 2:
            data = data.reshape(-1, data.shape[-1])
        data = data[:, :2] if data.shape[1] > 2 else data
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(RECORD_DIR, f"rec_{stamp}.wav")
        self._save_wav(path, data)
        name = f"rec_{stamp}  ({data.shape[0]/SAMPLE_RATE:.1f}s)"
        self.records.append((path, name))
        self.listbox.insert(END, name)
        self.listbox.selection_clear(0, END)
        self.listbox.selection_set(END)
        self.listbox.activate(END)
        self._on_select()
        self.status.set(self.t("saved").format(name))

    # ---------- WAV ----------
    @staticmethod
    def _save_wav(path, data):
        d = np.asarray(data)
        if d.dtype != np.int16:
            d = (np.clip(d, -1.0, 1.0) * 32767).astype(np.int16)
        if d.ndim == 1:
            d = d.reshape(-1, 1)
        d = d[:, :2] if d.shape[1] > 2 else d
        with wave.open(path, "wb") as w:
            w.setnchannels(d.shape[1])
            w.setsampwidth(2)
            w.setframerate(SAMPLE_RATE)
            w.writeframes(d.tobytes())

    @staticmethod
    def _read_wav(path):
        with wave.open(path, "rb") as w:
            nch, sw, fr, nframes = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
            raw = w.readframes(nframes)
        if sw == 2:
            dtype = np.int16
        elif sw == 1:
            dtype = np.uint8
        elif sw == 4:
            dtype = np.int32
        else:
            raise ValueError(f"unsupported width {sw}")
        data = np.frombuffer(raw, dtype=dtype).astype(np.float32)
        if sw == 1:
            data = (data - 128) / 128.0
        else:
            data = data / (2 ** (8 * sw - 1))
        data = data.reshape(-1, nch)
        return data, fr

    # ---------- 列表 ----------
    def _on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            self.cur = None
            self._cur_dur = None
            self._update_duration_label()
            return
        idx = sel[0]
        self.cur = self.records[idx][0]
        try:
            data, fr = self._read_wav(self.cur)
            self._cur_dur = len(data) / fr
            self._cur_fr = fr
            self._update_duration_label()
            self.var_end.set(f"{self._cur_dur:.1f}")
        except Exception as e:
            self.dur_label.config(text=self.t("read_fail").format(e))

    # ---------- 播放 ----------
    def _play_selected(self):
        if not self.cur:
            messagebox.showinfo(self.t("app_title"), self.t("select_first"))
            return
        if not self.ffmpeg:
            messagebox.showwarning(self.t("app_title"), self.t("no_ffmpeg_play"))
            return
        try:
            os.startfile(self.cur)
        except Exception as e:
            print("play fail", e)

    # ---------- 删除 ----------
    def _delete_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        path, name = self.records.pop(idx)
        self.listbox.delete(idx)
        try:
            os.remove(path)
        except Exception:
            pass
        self.cur = None
        self._cur_dur = None
        self._update_duration_label()

    def _clear_all(self):
        for path, _ in self.records:
            try:
                os.remove(path)
            except Exception:
                pass
        self.records.clear()
        self.listbox.delete(0, END)
        self.cur = None
        self._cur_dur = None
        self._update_duration_label()

    # ---------- 裁剪 ----------
    def _cut_preview(self):
        if not self.cur:
            messagebox.showinfo(self.t("app_title"), self.t("select_first"))
            return
        data, fr = self._read_wav(self.cur)
        total = len(data) / fr
        s = self._parse_sec(self.var_start.get()) or 0
        e = self._parse_sec(self.var_end.get())
        if e is None:
            e = total
        s, e = max(0, s), min(total, e)
        if e <= s:
            messagebox.showinfo(self.t("app_title"), self.t("invalid_range"))
            return
        messagebox.showinfo(self.t("app_title"), self.t("cut_preview").format(s, e, e - s))

    @staticmethod
    def _parse_sec(s):
        try:
            return float(s)
        except Exception:
            return None

    def _apply_cut(self):
        if not self.cur:
            messagebox.showinfo(self.t("app_title"), self.t("select_first"))
            return
        data, fr = self._read_wav(self.cur)
        total = len(data) / fr
        s = self._parse_sec(self.var_start.get()) or 0
        e = self._parse_sec(self.var_end.get())
        if e is None:
            e = total
        s, e = max(0, s), min(total, e)
        if e <= s:
            messagebox.showinfo(self.t("app_title"), self.t("invalid_range"))
            return
        seg = data[int(s * fr): int(e * fr)]
        path = self.cur
        self._save_wav(path, seg)
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0]
            newname = f"{os.path.basename(path)}  (trim {len(seg)/fr:.1f}s)"
            self.records[idx] = (path, newname)
            self.listbox.delete(idx)
            self.listbox.insert(idx, newname)
            self.listbox.selection_set(idx)
        self._on_select()
        self.status.set(self.t("cut_applied"))

    # ---------- 导出 MP3 ----------
    def export_mp3(self):
        if not self.cur:
            messagebox.showinfo(self.t("app_title"), self.t("select_first"))
            return
        if not self.ffmpeg:
            messagebox.showwarning(self.t("app_title"), self.t("no_ffmpeg_export"))
            return
        out = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 audio", "*.mp3")],
            initialfile=os.path.splitext(os.path.basename(self.cur))[0] + ".mp3",
            title=self.t("export_mp3"),
        )
        if not out:
            return
        data, fr = self._read_wav(self.cur)
        total = len(data) / fr
        s = self._parse_sec(self.var_start.get()) or 0
        e = self._parse_sec(self.var_end.get())
        if e is None:
            e = total
        s, e = max(0, s), min(total, e)
        tmp = self.cur
        if e > s and (s > 0 or e < total):
            seg = data[int(s * fr): int(e * fr)]
            tmp = os.path.join(RECORD_DIR, "_export_tmp.wav")
            self._save_wav(tmp, seg)
        self.status.set(self.t("exporting"))
        threading.Thread(target=self._do_export, args=(tmp, out), daemon=True).start()

    def _do_export(self, src, out):
        try:
            cmd = [self.ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", src,
                   "-codec:a", "libmp3lame", "-q:a", "2", out]
            r = subprocess.run(cmd, capture_output=True, timeout=180)
            if r.returncode != 0:
                self.status.set(self.t("export_fail"))
                err = r.stderr.decode("utf-8", "ignore")
                self.root.after(0, lambda: messagebox.showerror(self.t("app_title"), self.t("export_fail_detail").format(err)))
                return
            self.root.after(0, lambda: messagebox.showinfo(self.t("app_title"), self.t("export_done").format(out)))
            self.status.set(self.t("status_ready"))
        except Exception as e:
            self.status.set(self.t("export_fail"))
            self.root.after(0, lambda: messagebox.showerror(self.t("app_title"), self.t("export_err").format(e)))
        finally:
            tmp = os.path.join(RECORD_DIR, "_export_tmp.wav")
            if os.path.exists(tmp) and src == tmp:
                try:
                    os.remove(tmp)
                except Exception:
                    pass


def main():
    root = Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
