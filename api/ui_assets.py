"""Inline UI assets used by the local debug page."""

INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Standalone Deep Agents</title>
  <style>
    :root {
      --bg: #f4f1ea;
      --card: #fffdf8;
      --ink: #1f2937;
      --muted: #6b7280;
      --line: #d6d3d1;
      --accent: #9a3412;
      --accent-2: #7c2d12;
      --shadow: 0 12px 28px rgba(28, 25, 23, 0.08);
      --ok: #166534;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(154, 52, 18, 0.10), transparent 28%),
        radial-gradient(circle at top right, rgba(120, 53, 15, 0.08), transparent 24%),
        linear-gradient(180deg, #f7f4ed 0%, var(--bg) 100%);
    }
    .page { max-width: 1080px; margin: 0 auto; padding: 28px 20px 40px; }
    .hero { display: flex; justify-content: space-between; gap: 20px; align-items: flex-end; margin-bottom: 20px; }
    .hero h1 { margin: 0; font-size: 32px; }
    .hero p { margin: 8px 0 0; color: var(--muted); max-width: 720px; line-height: 1.6; }
    .pill { padding: 8px 12px; border-radius: 999px; background: rgba(154, 52, 18, 0.08); color: var(--accent-2); font-size: 13px; }
    .grid { display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 18px; }
    .card { background: var(--card); border: 1px solid rgba(214, 211, 209, 0.9); border-radius: 18px; box-shadow: var(--shadow); overflow: hidden; }
    .card-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 18px 12px; border-bottom: 1px solid rgba(214, 211, 209, 0.75); }
    .card-title { margin: 0; font-size: 18px; font-weight: 700; }
    .card-body { padding: 16px 18px 18px; }
    .stack { display: flex; flex-direction: column; gap: 12px; }
    label { display: block; margin-bottom: 6px; font-size: 13px; color: var(--muted); }
    input[type="text"], textarea {
      width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--line);
      background: white; color: var(--ink); font-size: 14px;
    }
    textarea { min-height: 140px; resize: vertical; line-height: 1.6; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .actions { display: flex; gap: 10px; flex-wrap: wrap; }
    button { border: 0; border-radius: 12px; padding: 11px 16px; background: var(--accent); color: white; font-weight: 600; cursor: pointer; }
    button.secondary { background: #57534e; }
    button.ghost { background: #ebe7df; color: var(--ink); }
    .output {
      border-radius: 14px; border: 1px solid rgba(214, 211, 209, 0.9); background: #fff;
      padding: 14px; min-height: 120px; white-space: pre-wrap; line-height: 1.6; font-size: 14px; overflow: auto;
    }
    .status-box {
      border-radius: 14px; border: 1px solid rgba(214, 211, 209, 0.9); background: #fff;
      padding: 14px; line-height: 1.6; font-size: 14px;
    }
    .footer-note { margin-top: 18px; font-size: 13px; color: var(--muted); }
    @media (max-width: 980px) {
      .grid { grid-template-columns: 1fr; }
      .hero { flex-direction: column; align-items: flex-start; }
      .row { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="page">
    <div class="hero">
      <div>
        <h1>Standalone Deep Agents</h1>
        <p>一个独立的 LangChain + Deep Agents 服务联调页，支持健康检查、普通聊天和流式聊天，直接连接当前目录下的 FastAPI 服务。</p>
      </div>
      <div class="pill" id="apiBaseLabel">API Base: /api/v1</div>
    </div>
    <div class="grid">
      <div class="stack">
        <section class="card">
          <div class="card-header"><h2 class="card-title">健康检查</h2></div>
          <div class="card-body stack">
            <div class="actions"><button id="healthBtn">检查 /health</button></div>
            <div class="output" id="healthOutput">点击按钮后显示结果</div>
          </div>
        </section>
        <section class="card">
          <div class="card-header"><h2 class="card-title">聊天测试</h2></div>
          <div class="card-body stack">
            <div>
              <label for="chatMessage">问题</label>
              <textarea id="chatMessage">请先拆解一个企业知识问答系统的开发任务，再给出实施建议。</textarea>
            </div>
            <div class="row">
              <div>
                <label for="conversationId">Conversation ID</label>
                <input id="conversationId" type="text" placeholder="可选，不填则自动生成" />
              </div>
              <div>
                <label for="chatModel">模型偏好</label>
                <input id="chatModel" type="text" placeholder="可选，例如 qwen3-32b" />
              </div>
            </div>
            <div class="actions">
              <button id="chatBtn">普通聊天</button>
              <button id="streamBtn" class="secondary">流式聊天</button>
              <button id="clearBtn" class="ghost">清空输出</button>
            </div>
            <div class="output" id="chatOutput">这里显示 /chat 或 /chat/stream 的结果</div>
          </div>
        </section>
      </div>
      <div class="stack">
        <section class="card">
          <div class="card-header"><h2 class="card-title">服务状态</h2></div>
          <div class="card-body stack">
            <div class="status-box" id="serviceStatus">
              页面初始化中...
            </div>
            <div class="actions">
              <button id="docsBtn" class="ghost">打开 Swagger</button>
            </div>
          </div>
        </section>
        <section class="card">
          <div class="card-header"><h2 class="card-title">说明</h2></div>
          <div class="card-body stack">
            <div class="status-box">
              <div>1. 先点健康检查确认服务可用</div>
              <div>2. 再测试普通聊天</div>
              <div>3. 最后测试流式聊天，看是否逐步返回内容</div>
            </div>
          </div>
        </section>
      </div>
    </div>
    <div class="footer-note">如果流式输出没有内容，请优先查看后端日志和浏览器开发者工具中的 Network 结果。</div>
  </div>
  <script src="/ui.js?v=1"></script>
</body>
</html>
"""


UI_JS = r"""
(function () {
  var apiBase = "/api/v1";
  function $(id) { return document.getElementById(id); }

  function setStatus(text) {
    $("serviceStatus").textContent = text;
  }

  function pretty(data) {
    if (typeof data === "string") { return data; }
    try { return JSON.stringify(data, null, 2); }
    catch (err) { return String(data); }
  }

  async function readJsonSafely(resp) {
    var text = await resp.text();
    try { return JSON.parse(text); }
    catch (err) { return text; }
  }

  function buildPayload() {
    var message = $("chatMessage").value.trim();
    var conversationId = $("conversationId").value.trim();
    var model = $("chatModel").value.trim();
    var payload = { messages: [{ role: "user", content: message }] };
    if (conversationId) { payload.conversation_id = conversationId; }
    if (model) { payload.model = model; }
    return payload;
  }

  $("apiBaseLabel").textContent = "API Base: " + apiBase;

  $("healthBtn").addEventListener("click", async function () {
    setStatus("正在检查服务健康状态...");
    $("healthOutput").textContent = "检查中...";
    try {
      var resp = await fetch(apiBase + "/health");
      var data = await readJsonSafely(resp);
      $("healthOutput").textContent = pretty(data);
      setStatus("健康检查请求已完成");
    } catch (err) {
      $("healthOutput").textContent = "请求失败: " + err;
      setStatus("健康检查请求失败");
    }
  });

  $("chatBtn").addEventListener("click", async function () {
    var payload = buildPayload();
    if (!payload.messages[0].content) {
      $("chatOutput").textContent = "请输入问题";
      return;
    }
    setStatus("正在请求普通聊天接口...");
    $("chatOutput").textContent = "请求中...";
    try {
      var resp = await fetch(apiBase + "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      var data = await readJsonSafely(resp);
      $("chatOutput").textContent = pretty(data);
      setStatus("普通聊天请求已完成");
    } catch (err) {
      $("chatOutput").textContent = "请求失败: " + err;
      setStatus("普通聊天请求失败");
    }
  });

  $("streamBtn").addEventListener("click", async function () {
    var payload = buildPayload();
    if (!payload.messages[0].content) {
      $("chatOutput").textContent = "请输入问题";
      return;
    }
    setStatus("正在请求流式聊天接口...");
    $("chatOutput").textContent = "流式请求中...\n";
    try {
      var resp = await fetch(apiBase + "/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!resp.body) {
        $("chatOutput").textContent = "当前浏览器不支持流式读取";
        setStatus("浏览器不支持流式读取");
        return;
      }

      var reader = resp.body.getReader();
      var decoder = new TextDecoder("utf-8");
      var buffer = "";

      while (true) {
        var result = await reader.read();
        if (result.done) { break; }
        buffer += decoder.decode(result.value, { stream: true });
        var parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (var i = 0; i < parts.length; i += 1) {
          var part = parts[i];
          if (part.indexOf("data: ") !== 0) { continue; }
          var raw = part.slice(6);
          try {
            var data = JSON.parse(raw);
            if (data.content) {
              $("chatOutput").textContent += data.content;
            } else if (data.done) {
              $("chatOutput").textContent += "\n\n[done]";
            } else if (data.error) {
              $("chatOutput").textContent += "\n\n[error] " + data.error;
            }
          } catch (err) {
            $("chatOutput").textContent += "\n" + raw;
          }
        }
      }
      setStatus("流式聊天请求已完成");
    } catch (err) {
      $("chatOutput").textContent += "\n请求失败: " + err;
      setStatus("流式聊天请求失败");
    }
  });

  $("clearBtn").addEventListener("click", function () {
    $("chatOutput").textContent = "这里显示 /chat 或 /chat/stream 的结果";
    setStatus("已清空输出");
  });

  $("docsBtn").addEventListener("click", function () {
    window.open("/docs", "_blank");
  });

  setStatus("页面初始化完成，按钮事件已绑定");
})();
"""
