class Analytics {
  constructor(endpoint) {
    this.endpoint = endpoint;
    this.queue = [];
    this.userId = null;
    this.anonymousId = this._getOrCreateAnonId();
    this.sessionId = crypto.randomUUID();

    setInterval(() => this.flush(), 5000);
    window.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") this.flush();
    });
  }

  identify(userId) {
    this.userId = userId;
  }

  track(eventName, properties = {}) {
    this.queue.push({
      event_id: crypto.randomUUID(),
      event_name: eventName,
      event_type: "track",
      timestamp: new Date().toISOString(),
      anonymous_id: this.anonymousId,
      user_id: this.userId,
      session_id: this.sessionId,
      context: this._buildContext(),
      properties,
    });
    if (this.queue.length >= 20) this.flush();
  }

  page(properties = {}) {
    this.track("page_viewed", { ...this._buildContext().page, ...properties });
  }

  flush() {
    if (this.queue.length === 0) return;
    const batch = this.queue.splice(0);
    const body = JSON.stringify({ batch, sent_at: new Date().toISOString() });

    fetch(this.endpoint, {
      method: "POST",
      body,
      keepalive: true,
      headers: { "Content-Type": "application/json" },
    });
  }

  _getOrCreateAnonId() {
    let id = localStorage.getItem("anonymous_id");
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem("anonymous_id", id);
    }
    return id;
  }

  _buildContext() {
    return {
      page: {
        url: window.location.href,
        path: window.location.pathname,
        referrer: document.referrer || null,
        title: document.title || null,
      },
      user_agent: navigator.userAgent,
      locale: navigator.language,
      screen: {
        width: window.screen.width,
        height: window.screen.height,
      },
    };
  }
}

export const analytics = new Analytics("/api/p");
