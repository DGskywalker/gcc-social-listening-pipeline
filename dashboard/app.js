/**
 * GCC Social Listening Dashboard - Interactive Client Application
 * Connects to pipeline dataset, renders Chart.js visualizations, manages filtering,
 * pagination, and CSV export.
 */

(function () {
  "use strict";

  // State Management
  const state = {
    allPosts: [],
    filteredPosts: [],
    trendsData: {},
    executiveSummary: {},
    currentPage: 1,
    pageSize: 8,
    charts: {},
    activeTheme: localStorage.getItem("gcc_theme") || "dark",
  };

  // Color tokens
  const colors = {
    positive: "#10b981",
    negative: "#ef4444",
    neutral: "#94a3b8",
    gold: "#f59e0b",
    blue: "#3b82f6",
    purple: "#8b5cf6",
    cyan: "#06b6d4",
    brands: [
      "#3b82f6", // Al-Noor (Blue)
      "#f59e0b", // DesertPay (Gold)
      "#10b981", // Oasis Retail (Green)
      "#ef4444", // Falcon Ride (Red)
      "#8b5cf6", // GulfCloud (Purple)
    ],
  };

  // DOM Elements
  const elements = {
    brandFilter: document.getElementById("brandFilter"),
    platformFilter: document.getElementById("platformFilter"),
    languageFilter: document.getElementById("languageFilter"),
    sentimentFilter: document.getElementById("sentimentFilter"),
    searchInput: document.getElementById("searchInput"),
    resetFiltersBtn: document.getElementById("resetFiltersBtn"),
    themeToggleBtn: document.getElementById("themeToggleBtn"),
    exportCsvBtn: document.getElementById("exportCsvBtn"),
    insightsContainer: document.getElementById("insightsContainer"),
    execTimestamp: document.getElementById("execTimestamp"),
    kpiTotalMentions: document.getElementById("kpiTotalMentions"),
    kpiNetSentiment: document.getElementById("kpiNetSentiment"),
    kpiLeadingBrand: document.getElementById("kpiLeadingBrand"),
    kpiLeadingBrandShare: document.getElementById("kpiLeadingBrandShare"),
    kpiActiveAlerts: document.getElementById("kpiActiveAlerts"),
    postsTableBody: document.getElementById("postsTableBody"),
    visibleCountBadge: document.getElementById("visibleCountBadge"),
    prevPageBtn: document.getElementById("prevPageBtn"),
    nextPageBtn: document.getElementById("nextPageBtn"),
    pageIndicator: document.getElementById("pageIndicator"),
  };

  // Initialize Application
  async function init() {
    applyTheme(state.activeTheme);
    setupEventListeners();
    await loadData();
    renderAll();
  }

  // Load Data: Try fetching data.json, fallback to sample_data.js
  async function loadData() {
    try {
      const response = await fetch("data.json");
      if (response.ok) {
        const data = await response.json();
        populateState(data);
        return;
      }
    } catch (e) {
      console.warn("Could not fetch data.json via HTTP; falling back to embedded sample_data.js", e);
    }

    if (window.SOCIAL_LISTENING_DATA) {
      populateState(window.SOCIAL_LISTENING_DATA);
    } else {
      console.error("No social listening data source found.");
    }
  }

  function populateState(data) {
    state.allPosts = data.posts || [];
    state.filteredPosts = [...state.allPosts];
    state.trendsData = data.trends_data || {};
    state.executiveSummary = data.executive_summary || {};
  }

  // Event Listeners
  function setupEventListeners() {
    elements.brandFilter.addEventListener("change", applyFilters);
    elements.platformFilter.addEventListener("change", applyFilters);
    elements.languageFilter.addEventListener("change", applyFilters);
    elements.sentimentFilter.addEventListener("change", applyFilters);
    
    // Debounced search
    let searchTimeout;
    elements.searchInput.addEventListener("input", () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(applyFilters, 250);
    });

    elements.resetFiltersBtn.addEventListener("click", resetFilters);
    elements.themeToggleBtn.addEventListener("click", toggleTheme);
    elements.exportCsvBtn.addEventListener("click", exportFilteredCSV);

    elements.prevPageBtn.addEventListener("click", () => {
      if (state.currentPage > 1) {
        state.currentPage--;
        renderTable();
      }
    });

    elements.nextPageBtn.addEventListener("click", () => {
      const maxPages = Math.ceil(state.filteredPosts.length / state.pageSize) || 1;
      if (state.currentPage < maxPages) {
        state.currentPage++;
        renderTable();
      }
    });
  }

  // Theme Management
  function applyTheme(theme) {
    state.activeTheme = theme;
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("gcc_theme", theme);
    elements.themeToggleBtn.textContent = theme === "dark" ? "☀️" : "🌙";
    elements.themeToggleBtn.setAttribute("aria-label", `Switch to ${theme === "dark" ? "light" : "dark"} theme`);
  }

  function toggleTheme() {
    const nextTheme = state.activeTheme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
    // Re-render charts with updated theme defaults
    renderCharts();
  }

  // Filtering Logic
  function applyFilters() {
    const brand = elements.brandFilter.value;
    const platform = elements.platformFilter.value;
    const language = elements.languageFilter.value;
    const sentiment = elements.sentimentFilter.value;
    const query = elements.searchInput.value.trim().toLowerCase();

    state.filteredPosts = state.allPosts.filter((post) => {
      // Brand filter
      if (brand !== "ALL" && post.brand !== brand) return false;

      // Platform filter
      if (platform !== "ALL") {
        if (!post.source.toLowerCase().includes(platform.toLowerCase())) return false;
      }

      // Language filter
      if (language !== "ALL" && post.language !== language) return false;

      // Sentiment filter
      if (sentiment !== "ALL" && post.sentiment !== sentiment) return false;

      // Text search
      if (query) {
        const textMatch = (post.text || "").toLowerCase().includes(query);
        const authorMatch = (post.author || "").toLowerCase().includes(query);
        const themeMatch = (post.primary_theme || "").toLowerCase().includes(query);
        if (!textMatch && !authorMatch && !themeMatch) return false;
      }

      return true;
    });

    state.currentPage = 1;
    renderAll();
  }

  function resetFilters() {
    elements.brandFilter.value = "ALL";
    elements.platformFilter.value = "ALL";
    elements.languageFilter.value = "ALL";
    elements.sentimentFilter.value = "ALL";
    elements.searchInput.value = "";
    applyFilters();
  }

  // Master Render
  function renderAll() {
    renderExecutiveSummary();
    updateKPIs();
    renderCharts();
    renderTable();
  }

  // 1. Executive Summary Rendering
  function renderExecutiveSummary() {
    const summary = state.executiveSummary;
    if (summary.generated_at) {
      elements.execTimestamp.textContent = `Generated: ${summary.generated_at}`;
    }

    const container = elements.insightsContainer;
    container.innerHTML = "";

    const insights = summary.insights || [
      {
        type: "outage_alert",
        title: "🚨 Al-Noor Telecom 5G Outage Flare-Up",
        body: "Al-Noor Telecom experienced a 44% spike in negative mentions centered in Northern Riyadh (Al-Yasmin district). Sarcastic complaints indicate customer dissatisfaction with chatbot deflection.",
        action: "Dispatch network engineering teams to inspect Al-Yasmin cell towers; publish an official SLA incident notification."
      },
      {
        type: "promotional_win",
        title: "💡 DesertPay Cashback Campaign Dominance",
        body: "DesertPay generated 78% positive sentiment with its 10% instant Ramadan supermarket cashback offer. Share of voice rose to 28% of total GCC fintech discussions.",
        action: "Scale creator partnerships across Saudi & UAE retail accounts to capture active wallet migrations."
      },
      {
        type: "pricing_risk",
        title: "⚠️ Falcon Ride Surge Pricing Friction",
        body: "Falcon Ride faced consumer pushback on weekend surge multipliers (reaching 2.8x base fare in Riyadh Boulevard and Dubai), driving users toward competing apps.",
        action: "Cap maximum surge multipliers during cultural events and review driver commission structures."
      }
    ];

    insights.forEach((ins) => {
      const card = document.createElement("article");
      const cardClass = ins.type === "outage_alert" ? "alert" : (ins.type === "promotional_win" ? "win" : "risk");
      card.className = `insight-card ${cardClass}`;
      card.innerHTML = `
        <h3>${ins.title}</h3>
        <p>${ins.body}</p>
        <div class="action-box">
          <strong>Recommended Action:</strong> ${ins.action}
        </div>
      `;
      container.appendChild(card);
    });
  }

  // 2. Key Metrics KPIs
  function updateKPIs() {
    const posts = state.filteredPosts;
    const total = posts.length;

    elements.kpiTotalMentions.textContent = total.toLocaleString();

    // Net Sentiment (NPS proxy: % Positive - % Negative)
    const pos = posts.filter((p) => p.sentiment === "positive").length;
    const neg = posts.filter((p) => p.sentiment === "negative").length;
    const netSentiment = total > 0 ? Math.round(((pos - neg) / total) * 100) : 0;
    
    elements.kpiNetSentiment.textContent = `${netSentiment > 0 ? "+" : ""}${netSentiment}%`;
    elements.kpiNetSentiment.className = `kpi-value ${netSentiment >= 0 ? "positive-text" : "warning-text"}`;

    // Share of Voice
    const brandCounts = {};
    posts.forEach((p) => {
      brandCounts[p.brand] = (brandCounts[p.brand] || 0) + 1;
    });

    let topBrand = "--";
    let topShare = 0;
    for (const [b, count] of Object.entries(brandCounts)) {
      if (count > topShare) {
        topBrand = b;
        topShare = count;
      }
    }
    elements.kpiLeadingBrand.textContent = topBrand;
    elements.kpiLeadingBrandShare.textContent = total > 0 ? `${Math.round((topShare / total) * 100)}% of filtered volume` : "--";

    // Active Operational Outages
    const outages = posts.filter((p) => p.primary_theme === "Network & Outage" && p.sentiment === "negative").length;
    elements.kpiActiveAlerts.textContent = outages;
  }

  // 3. Visualizations (Chart.js)
  function renderCharts() {
    const isDark = state.activeTheme === "dark";
    const textColor = isDark ? "#9ca3af" : "#475569";
    const gridColor = isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)";

    // Default chart font
    Chart.defaults.color = textColor;
    Chart.defaults.font.family = "'Inter', system-ui, sans-serif";

    renderSOVChart(gridColor, textColor);
    renderSentimentTrendChart(gridColor, textColor);
    renderThemesChart(gridColor, textColor);
    renderTrendsOverlayChart(gridColor, textColor);
  }

  // Chart 1: Share of Voice
  function renderSOVChart(gridColor, textColor) {
    const ctx = document.getElementById("sovChart").getContext("2d");
    if (state.charts.sov) state.charts.sov.destroy();

    const brandCounts = {};
    state.filteredPosts.forEach((p) => {
      brandCounts[p.brand] = (brandCounts[p.brand] || 0) + 1;
    });

    const labels = Object.keys(brandCounts);
    const data = Object.values(brandCounts);

    state.charts.sov = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels.length ? labels : ["No data"],
        datasets: [{
          data: data.length ? data : [1],
          backgroundColor: colors.brands.slice(0, labels.length),
          borderWidth: 2,
          borderColor: state.activeTheme === "dark" ? "#111827" : "#ffffff",
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "right", labels: { boxWidth: 12, padding: 14 } },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.label}: ${ctx.raw} mentions (${Math.round((ctx.raw / (state.filteredPosts.length || 1)) * 100)}%)`,
            }
          }
        },
        cutout: "68%",
      }
    });
  }

  // Chart 2: Sentiment Trend Over Time
  function renderSentimentTrendChart(gridColor, textColor) {
    const ctx = document.getElementById("sentimentTrendChart").getContext("2d");
    if (state.charts.sentimentTrend) state.charts.sentimentTrend.destroy();

    // Group posts by date
    const dateMap = {};
    state.filteredPosts.forEach((p) => {
      const d = p.date || p.published_at.slice(0, 10);
      if (!dateMap[d]) dateMap[d] = { positive: 0, negative: 0, neutral: 0 };
      if (dateMap[d][p.sentiment] !== undefined) {
        dateMap[d][p.sentiment]++;
      }
    });

    const sortedDates = Object.keys(dateMap).sort().slice(-14); // Last 14 days
    const posData = sortedDates.map((d) => dateMap[d].positive);
    const negData = sortedDates.map((d) => dateMap[d].negative);
    const neuData = sortedDates.map((d) => dateMap[d].neutral);

    state.charts.sentimentTrend = new Chart(ctx, {
      type: "line",
      data: {
        labels: sortedDates.map((d) => d.slice(5)), // MM-DD
        datasets: [
          {
            label: "Positive",
            data: posData,
            borderColor: colors.positive,
            backgroundColor: "rgba(16, 185, 129, 0.1)",
            tension: 0.35,
            fill: true,
            borderWidth: 2,
          },
          {
            label: "Negative",
            data: negData,
            borderColor: colors.negative,
            backgroundColor: "rgba(239, 68, 68, 0.1)",
            tension: 0.35,
            fill: true,
            borderWidth: 2,
          },
          {
            label: "Neutral",
            data: neuData,
            borderColor: colors.neutral,
            backgroundColor: "transparent",
            borderDash: [4, 4],
            tension: 0.35,
            borderWidth: 1.5,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        scales: {
          x: { grid: { color: gridColor }, ticks: { font: { size: 11 } } },
          y: { grid: { color: gridColor }, beginAtZero: true, ticks: { precision: 0 } },
        },
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12, padding: 12 } },
        }
      }
    });
  }

  // Chart 3: Top Themes Horizontal Bar
  function renderThemesChart(gridColor, textColor) {
    const ctx = document.getElementById("themesChart").getContext("2d");
    if (state.charts.themes) state.charts.themes.destroy();

    const themeCounts = {};
    state.filteredPosts.forEach((p) => {
      const th = p.primary_theme || "General";
      themeCounts[th] = (themeCounts[th] || 0) + 1;
    });

    const sortedThemes = Object.entries(themeCounts).sort((a, b) => b[1] - a[1]);
    const labels = sortedThemes.map((t) => t[0]);
    const counts = sortedThemes.map((t) => t[1]);

    state.charts.themes = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Volume",
          data: counts,
          backgroundColor: labels.map((th) => th === "Network & Outage" ? colors.negative : (th === "Promotions & Offers" ? colors.positive : colors.blue)),
          borderRadius: 4,
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: gridColor }, beginAtZero: true, ticks: { precision: 0 } },
          y: { grid: { display: false } },
        },
        plugins: {
          legend: { display: false },
        }
      }
    });
  }

  // Chart 4: Google Trends vs Social Volume Overlay
  function renderTrendsOverlayChart(gridColor, textColor) {
    const ctx = document.getElementById("trendsOverlayChart").getContext("2d");
    if (state.charts.trendsOverlay) state.charts.trendsOverlay.destroy();

    const selectedBrand = elements.brandFilter.value !== "ALL" ? elements.brandFilter.value : "Al-Noor Telecom";
    const brandTrends = state.trendsData[selectedBrand] || [];

    // Aggregate social volume by date for this brand
    const socialDateMap = {};
    state.filteredPosts
      .filter((p) => p.brand === selectedBrand)
      .forEach((p) => {
        const d = p.date || p.published_at.slice(0, 10);
        socialDateMap[d] = (socialDateMap[d] || 0) + 1;
      });

    const recentTrends = brandTrends.slice(-14);
    const labels = recentTrends.map((t) => t.date.slice(5));
    const searchScores = recentTrends.map((t) => t.score);
    const socialCounts = recentTrends.map((t) => socialDateMap[t.date] || 0);

    state.charts.trendsOverlay = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels.length ? labels : ["No data"],
        datasets: [
          {
            label: `Google Search Index (${selectedBrand})`,
            data: searchScores,
            borderColor: colors.blue,
            backgroundColor: "transparent",
            borderWidth: 2,
            yAxisID: "ySearch",
            tension: 0.3,
          },
          {
            type: "bar",
            label: "Social Mentions",
            data: socialCounts,
            backgroundColor: "rgba(245, 158, 11, 0.4)",
            borderColor: colors.gold,
            borderWidth: 1,
            borderRadius: 3,
            yAxisID: "ySocial",
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: gridColor } },
          ySearch: {
            type: "linear",
            position: "left",
            grid: { color: gridColor },
            title: { display: true, text: "Google Search Index (0-100)" },
            min: 0,
            max: 100,
          },
          ySocial: {
            type: "linear",
            position: "right",
            grid: { display: false },
            title: { display: true, text: "Social Volume" },
            beginAtZero: true,
            ticks: { precision: 0 },
          }
        },
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12 } },
        }
      }
    });
  }

  // 4. Feed Table Rendering & Pagination
  function renderTable() {
    const tableBody = elements.postsTableBody;
    tableBody.innerHTML = "";

    const posts = state.filteredPosts;
    const total = posts.length;
    const maxPages = Math.ceil(total / state.pageSize) || 1;

    elements.visibleCountBadge.textContent = `Showing ${total} posts`;
    elements.pageIndicator.textContent = `Page ${state.currentPage} of ${maxPages}`;
    elements.prevPageBtn.disabled = state.currentPage <= 1;
    elements.nextPageBtn.disabled = state.currentPage >= maxPages;

    if (total === 0) {
      tableBody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 2.5rem; color: var(--text-muted);">No social listening posts match the selected filters.</td></tr>`;
      return;
    }

    const startIdx = (state.currentPage - 1) * state.pageSize;
    const pagePosts = posts.slice(startIdx, startIdx + state.pageSize);

    pagePosts.forEach((post) => {
      const tr = document.createElement("tr");

      // Platform badge style
      let platformClass = "trends";
      let platformName = "Google Trends";
      if (post.source.includes("tiktok")) {
        platformClass = "tiktok";
        platformName = "TikTok";
      } else if (post.source.includes("instagram")) {
        platformClass = "instagram";
        platformName = "Instagram";
      } else if (post.source.includes("youtube")) {
        platformClass = "youtube";
        platformName = "YouTube";
      }

      // Sentiment pill style
      const sentClass = `badge-${post.sentiment}`;
      const sentIcon = post.sentiment === "positive" ? "▲" : (post.sentiment === "negative" ? "▼" : "●");

      // Text with Arabic direction support
      const isArabic = post.language === "ar" || /[\u0600-\u06FF]/.test(post.text);
      const textSpan = isArabic ? `<span class="arabic-text" dir="rtl">${escapeHTML(post.text)}</span>` : `<span>${escapeHTML(post.text)}</span>`;
      const sarcasmBadge = post.is_sarcasm ? `<span class="sarcasm-flag" title="Dialectal Sarcasm Detected">⚠️ Sarcasm</span>` : "";

      // Format engagement summary
      let engSummary = "-";
      if (post.engagement) {
        if (post.engagement.views) {
          engSummary = `👁️ ${post.engagement.views.toLocaleString()} · ❤️ ${post.engagement.likes.toLocaleString()}`;
        } else if (post.engagement.likes) {
          engSummary = `❤️ ${post.engagement.likes.toLocaleString()} · 💬 ${post.engagement.comments || 0}`;
        } else if (post.engagement.search_index !== undefined) {
          engSummary = `Trend: ${post.engagement.search_index}/100`;
        }
      }

      tr.innerHTML = `
        <td style="white-space: nowrap;">${post.date || post.published_at.slice(0, 10)}</td>
        <td>
          <span class="platform-pill ${platformClass}">${platformName}</span>
          ${post.is_synthetic ? '<span style="font-size: 0.68rem; color: var(--accent-gold); display:block; margin-top:2px;">Synthetic</span>' : ''}
        </td>
        <td style="font-weight: 600;">${escapeHTML(post.brand)}</td>
        <td class="post-text-cell">
          ${textSpan}
          ${sarcasmBadge}
        </td>
        <td>
          <span style="font-weight: 600;">${post.language.toUpperCase()}</span>
          <span style="color: var(--text-muted); font-size: 0.75rem; display:block;">${post.dialect || "-"}</span>
        </td>
        <td><span class="badge" style="background: var(--bg-tertiary);">${escapeHTML(post.primary_theme || "General")}</span></td>
        <td>
          <span class="badge ${sentClass}">
            ${sentIcon} ${post.sentiment.toUpperCase()}
          </span>
        </td>
        <td style="font-size: 0.8rem; white-space: nowrap; color: var(--text-secondary);">${engSummary}</td>
      `;
      tableBody.appendChild(tr);
    });
  }

  // 5. CSV Export
  function exportFilteredCSV() {
    const posts = state.filteredPosts;
    if (!posts.length) {
      alert("No posts to export.");
      return;
    }

    const headers = ["id", "source", "published_at", "brand", "language", "dialect", "primary_theme", "sentiment", "sentiment_score", "is_sarcasm", "text"];
    const rows = posts.map((p) => [
      p.id,
      p.source,
      p.published_at,
      p.brand,
      p.language,
      p.dialect || "",
      p.primary_theme,
      p.sentiment,
      p.sentiment_score,
      p.is_sarcasm ? "TRUE" : "FALSE",
      `"${(p.text || "").replace(/"/g, '""').replace(/\n/g, ' ')}"`,
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `gcc_social_listening_export_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // Helper: Escape HTML
  function escapeHTML(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Start app on DOMContentLoaded
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
