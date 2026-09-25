const state = {
    backendUrl:
        localStorage.getItem("atul_backend_url")
        || "http://127.0.0.1:8000",

    assets: [],
    sources: [],
    syncs: [],
    audits: [],

    currentView: "dashboard",

    assetPage: 1,
    assetPageSize: 10,

    refreshTimer: null,
    refreshSeconds: 30,
    refreshPaused: false,

    lastRefresh: null,
    scheduler: null,
    changes: {},

    loading: false
};


const $ = (id) =>
    document.getElementById(id);


function escapeHtml(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function showToast(
    message,
    type = "info"
) {
    const container =
        $("toastContainer");

    const toast =
        document.createElement("div");

    toast.className =
        `toast ${type}`;

    toast.innerHTML = `
        <div class="toast-dot"></div>
        <div>${escapeHtml(message)}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("closing");

        setTimeout(
            () => toast.remove(),
            300
        );
    }, 3500);
}


function openModal(
    title,
    body,
    footer = ""
) {
    $("modalTitle").textContent =
        title;

    $("modalBody").innerHTML =
        body;

    $("modalFooter").innerHTML =
        footer;

    $("modalBackdrop")
        .classList
        .remove("hidden");
}


function closeModal() {
    $("modalBackdrop")
        .classList
        .add("hidden");
}


async function api(
    path,
    options = {}
) {
    const url =
        state.backendUrl + path;

    const response =
        await fetch(
            url,
            {
                ...options,
                headers: {
                    "Content-Type":
                        "application/json",
                    ...(options.headers || {})
                }
            }
        );

    const text =
        await response.text();

    let data = {};

    try {
        data = text
            ? JSON.parse(text)
            : {};
    } catch {
        data = {
            raw: text
        };
    }

    if (!response.ok) {
        throw new Error(
            data.detail
            || data.message
            || `HTTP ${response.status}`
        );
    }

    return data;
}


function setConnection(
    online,
    text = null
) {
    const badge =
        $("connectionBadge");

    const live =
        $("liveText");

    if (online) {
        badge.className =
            "connection-badge online";

        badge.innerHTML =
            `<span class="pulse"></span>${text || "API CONNECTED"}`;

        live.textContent =
            "LIVE SYSTEM";

        $("backendStatus")
            .textContent =
            "ONLINE";
    } else {
        badge.className =
            "connection-badge offline";

        badge.innerHTML =
            `<span class="pulse"></span>${text || "API OFFLINE"}`;

        live.textContent =
            "OFFLINE";

        $("backendStatus")
            .textContent =
            "OFFLINE";
    }
}


async function loadRoot() {
    try {

        const data =
            await api("/");

        $("versionText")
            .textContent =
            data.version || "--";

        $("heroSystemStatus")
            .textContent =
            String(
                data.status || "UNKNOWN"
            ).toUpperCase();

        setConnection(
            true,
            "API CONNECTED"
        );

        return data;

    } catch (error) {

        setConnection(
            false,
            "API OFFLINE"
        );

        throw error;
    }
}


async function loadDatabase() {
    try {

        const data =
            await api(
                "/api/v1/health/database"
            );

        $("databaseStatus")
            .textContent =
            String(
                data.status || "unknown"
            ).toUpperCase();

        return data;

    } catch {

        $("databaseStatus")
            .textContent =
            "OFFLINE";
    }
}


async function loadAssets() {
    const params =
        new URLSearchParams();

    const search =
        $("assetSearch")?.value
        || "";

    const status =
        $("assetStatusFilter")?.value
        || "";

    const type =
        $("assetTypeFilter")?.value
        || "";

    const location =
        $("locationFilter")?.value
        || "";

    const owner =
        $("ownerFilter")?.value
        || "";

    const minValue =
        $("minValueFilter")?.value
        || "";

    const maxValue =
        $("maxValueFilter")?.value
        || "";

    params.set(
        "page",
        state.assetPage
    );

    params.set(
        "page_size",
        state.assetPageSize
    );

    if (search)
        params.set(
            "search",
            search
        );

    if (status)
        params.set(
            "asset_status",
            status
        );

    if (type)
        params.set(
            "asset_type",
            type
        );

    if (location)
        params.set(
            "location",
            location
        );

    if (owner)
        params.set(
            "owner",
            owner
        );

    if (minValue)
        params.set(
            "min_value",
            minValue
        );

    if (maxValue)
        params.set(
            "max_value",
            maxValue
        );

    try {

        const data =
            await api(
                `/api/v1/assets?${params}`
            );

        state.assets =
            data.assets || [];

        state.assetTotal =
            data.total || 0;

        renderAssets();

    } catch (error) {

        renderError(
            "assetTable",
            error.message
        );
    }
}


async function loadAllAssetsForAnalytics() {
    try {

        const data =
            await api(
                "/api/v1/assets?page=1&page_size=1000"
            );

        return data.assets || [];

    } catch {

        return state.assets;
    }
}


async function loadSources() {
    try {

        const data =
            await api(
                "/api/v1/automation/sources"
            );

        state.sources =
            data.sources || [];

        renderSources();
        renderDashboard();

        return state.sources;

    } catch (error) {

        renderError(
            "sourceCards",
            error.message
        );

        return [];
    }
}


async function loadSyncs() {
    try {

        const data =
            await api(
                "/api/v1/synchronization"
            );

        if (
            Array.isArray(data)
        ) {
            state.syncs =
                data;
        } else {
            state.syncs =
                data.records
                || data.sync_records
                || data.synchronizations
                || [];
        }

        renderSync();
        renderDashboard();

    } catch (error) {

        renderError(
            "syncTable",
            error.message
        );
    }
}


async function loadAudits() {
    try {

        const data =
            await api(
                "/api/v1/audit?limit=100"
            );

        state.audits =
            data.records
            || data.audit_logs
            || data.audits
            || [];

        renderAudit();

    } catch (error) {

        renderError(
            "auditTable",
            error.message
        );
    }
}


async function loadScheduler() {
    try {

        state.scheduler =
            await api(
                "/api/v1/automation/scheduler"
            );

        renderHealth();

    } catch {
        state.scheduler = null;
    }
}


async function loadChanges() {
    try {

        const data =
            await api(
                "/api/v1/automation/changes"
            );

        state.changes =
            data.cached_sources || {};

        renderHealth();

    } catch {
        state.changes = {};
    }
}


async function refreshAll(
    showMessage = false
) {
    if (state.loading)
        return;

    state.loading = true;

    try {

        await Promise.allSettled([
            loadRoot(),
            loadDatabase(),
            loadAssets(),
            loadSources(),
            loadSyncs(),
            loadAudits(),
            loadScheduler(),
            loadChanges()
        ]);

        const analyticsAssets =
            await loadAllAssetsForAnalytics();

        state.analyticsAssets =
            analyticsAssets;

        state.lastRefresh =
            new Date();

        renderDashboard();
        renderHealth();

        $("lastRefresh")
            .textContent =
            `Last refresh: ${state.lastRefresh.toLocaleTimeString()}`;

        if (showMessage) {
            showToast(
                "ATUL data refreshed.",
                "success"
            );
        }

    } finally {

        state.loading = false;
    }
}


function renderKpis() {

    const assets =
        state.analyticsAssets
        || state.assets;

    const active =
        assets.filter(
            x =>
                String(
                    x.status || ""
                ).toLowerCase()
                === "active"
        ).length;

    const maintenance =
        assets.filter(
            x =>
                String(
                    x.status || ""
                ).toLowerCase()
                === "maintenance"
        ).length;

    const locations =
        new Set(
            assets
                .map(
                    x => x.location
                )
                .filter(Boolean)
        ).size;

    const healthySources =
        state.sources.filter(
            source =>
                source.enabled !== false
        ).length;

    const failedSyncs =
        state.syncs.filter(
            sync =>
                String(
                    sync.status || ""
                ).toLowerCase()
                === "failed"
        ).length;

    const created =
        state.syncs.reduce(
            (
                total,
                item
            ) =>
                total +
                Number(
                    item.records_created
                    || 0
                ),
            0
        );

    const updated =
        state.syncs.reduce(
            (
                total,
                item
            ) =>
                total +
                Number(
                    item.records_updated
                    || 0
                ),
            0
        );

    const cards = [

        [
            "TOTAL ASSETS",
            assets.length,
            "Asset records",
            "asset"
        ],

        [
            "ACTIVE",
            active,
            "Operational assets",
            "good"
        ],

        [
            "MAINTENANCE",
            maintenance,
            "Attention required",
            "warning"
        ],

        [
            "LOCATIONS",
            locations,
            "Physical locations",
            "info"
        ],

        [
            "SOURCES",
            state.sources.length,
            "Connected sources",
            "source"
        ],

        [
            "ENABLED SOURCES",
            healthySources,
            "Active integrations",
            "good"
        ],

        [
            "SYNC OPERATIONS",
            state.syncs.length,
            "Recorded operations",
            "sync"
        ],

        [
            "SYNC FAILURES",
            failedSyncs,
            "Failed operations",
            failed
        ],

        [
            "CREATED BY SYNC",
            created,
            "Imported records",
            "good"
        ],

        [
            "UPDATED BY SYNC",
            updated,
            "Changed records",
            "info"
        ]

    ];

    $("kpiGrid").innerHTML =
        cards.map(
            card => `
                <div class="kpi-card ${card[3]}">
                    <div class="kpi-label">
                        ${card[0]}
                    </div>

                    <div class="kpi-value">
                        ${card[1]}
                    </div>

                    <div class="kpi-note">
                        ${card[2]}
                    </div>
                </div>
            `
        ).join("");
}


function renderDashboard() {

    renderKpis();

    const assets =
        state.analyticsAssets
        || state.assets;

    const statuses = {};

    assets.forEach(
        asset => {
            const key =
                asset.status
                || "unknown";

            statuses[key] =
                (statuses[key] || 0)
                + 1;
        }
    );

    const locations = {};

    assets.forEach(
        asset => {
            const key =
                asset.location
                || "Unknown";

            locations[key] =
                (locations[key] || 0)
                + 1;
        }
    );

    const owners = {};

    assets.forEach(
        asset => {
            const key =
                asset.owner
                || "Unknown";

            owners[key] =
                (owners[key] || 0)
                + 1;
        }
    );

    $("assetAnalytics").innerHTML = `
        <div class="analytics-card">
            <div class="analytics-title">
                STATUS DISTRIBUTION
            </div>

            ${renderBars(statuses)}
        </div>

        <div class="analytics-card">
            <div class="analytics-title">
                LOCATION DISTRIBUTION
            </div>

            ${renderBars(locations)}
        </div>

        <div class="analytics-card">
            <div class="analytics-title">
                OWNERSHIP DISTRIBUTION
            </div>

            ${renderBars(owners)}
        </div>
    `;

    $("sourceAnalytics").innerHTML =
        state.sources.length
        ? state.sources.map(
            source => `
                <div class="health-row">
                    <div>
                        <strong>
                            ${escapeHtml(
                                source.name
                                || source.id
                            )}
                        </strong>

                        <small>
                            ${escapeHtml(
                                source.type
                                || "HTTP"
                            )}
                        </small>
                    </div>

                    <span class="
                        status-pill
                        ${source.enabled === false
                            ? "disabled"
                            : "active"}
                    ">
                        ${
                            source.enabled === false
                            ? "DISABLED"
                            : "ENABLED"
                        }
                    </span>
                </div>
            `
        ).join("")
        : emptyState(
            "No sources connected."
        );

    renderSyncActivity();
    renderLiveActivity();
}


function renderBars(
    values
) {
    const entries =
        Object.entries(values);

    if (!entries.length) {
        return emptyState(
            "No data available."
        );
    }

    const max =
        Math.max(
            ...entries.map(
                x => x[1]
            ),
            1
        );

    return entries
        .slice(0, 8)
        .map(
            ([key, value]) => `
                <div class="bar-row">

                    <div class="bar-label">
                        ${escapeHtml(key)}
                    </div>

                    <div class="bar-track">
                        <div
                            class="bar-fill"
                            style="
                                width:
                                ${(value / max) * 100}%
                            "
                        ></div>
                    </div>

                    <div class="bar-value">
                        ${value}
                    </div>

                </div>
            `
        ).join("");
}


function renderSyncActivity() {

    const recent =
        [...state.syncs]
            .reverse()
            .slice(0, 8);

    $("syncActivity").innerHTML =
        recent.length
        ? recent.map(
            sync => `
                <div class="activity-row">

                    <div class="activity-icon">
                        ${sync.status === "failed"
                            ? "!"
                            : "↻"}
                    </div>

                    <div class="activity-content">

                        <strong>
                            ${escapeHtml(
                                sync.source_name
                                || sync.source
                                || "Synchronization"
                            )}
                        </strong>

                        <small>
                            ${escapeHtml(
                                sync.message
                                || sync.status
                                || "completed"
                            )}
                        </small>

                    </div>

                    <span class="
                        status-pill
                        ${
                            String(
                                sync.status || ""
                            ).toLowerCase()
                            === "failed"
                            ? "failed"
                            : "active"
                        }
                    ">
                        ${escapeHtml(
                            sync.status
                            || "unknown"
                        )}
                    </span>

                </div>
            `
        ).join("")
        : emptyState(
            "No synchronization activity yet."
        );
}


function renderLiveActivity() {

    const events = [];

    state.audits
        .slice(0, 5)
        .forEach(
            audit => {
                events.push({
                    title:
                        audit.action
                        || "AUDIT",
                    text:
                        audit.description
                        || audit.asset_code
                        || "Asset event",
                    date:
                        audit.created_at
                });
            }
        );

    state.syncs
        .slice(0, 5)
        .forEach(
            sync => {
                events.push({
                    title:
                        "SYNC",
                    text:
                        sync.source_name
                        || "Source",
                    date:
                        sync.completed_at
                        || sync.started_at
                });
            }
        );

    events.sort(
        (
            a,
            b
        ) =>
            new Date(
                b.date || 0
            )
            -
            new Date(
                a.date || 0
            )
    );

    $("liveActivity").innerHTML =
        events.length
        ? events
            .slice(0, 10)
            .map(
                event => `
                    <div class="activity-row">

                        <div class="activity-icon">
                            •
                        </div>

                        <div class="activity-content">

                            <strong>
                                ${escapeHtml(
                                    event.title
                                )}
                            </strong>

                            <small>
                                ${escapeHtml(
                                    event.text
                                )}
                            </small>

                        </div>

                        <small>
                            ${formatDate(
                                event.date
                            )}
                        </small>

                    </div>
                `
            ).join("")
        : emptyState(
            "No recent activity."
        );
}


function renderAssets() {

    const search =
        (
            $("assetSearch")
                ?.value
            || ""
        ).toLowerCase();

    const status =
        $("assetStatusFilter")
            ?.value
        || "";

    const type =
        (
            $("assetTypeFilter")
                ?.value
            || ""
        ).toLowerCase();

    const location =
        (
            $("locationFilter")
                ?.value
            || ""
        ).toLowerCase();

    const owner =
        (
            $("ownerFilter")
                ?.value
            || ""
        ).toLowerCase();

    const min =
        Number(
            $("minValueFilter")
                ?.value
            || 0
        );

    const max =
        Number(
            $("maxValueFilter")
                ?.value
            || Number.MAX_SAFE_INTEGER
        );

    let records =
        [...state.assets];

    records =
        records.filter(
            asset => {

                const haystack =
                    [
                        asset.asset_code,
                        asset.name,
                        asset.serial_number,
                        asset.description
                    ]
                    .join(" ")
                    .toLowerCase();

                const value =
                    Number(
                        asset.current_value
                        || asset.purchase_value
                        || 0
                    );

                return (
                    (
                        !search
                        ||
                        haystack.includes(
                            search
                        )
                    )
                    &&
                    (
                        !status
                        ||
                        asset.status
                        === status
                    )
                    &&
                    (
                        !type
                        ||
                        String(
                            asset.asset_type
                            || ""
                        )
                        .toLowerCase()
                        .includes(type)
                    )
                    &&
                    (
                        !location
                        ||
                        String(
                            asset.location
                            || ""
                        )
                        .toLowerCase()
                        .includes(location)
                    )
                    &&
                    (
                        !owner
                        ||
                        String(
                            asset.owner
                            || ""
                        )
                        .toLowerCase()
                        .includes(owner)
                    )
                    &&
                    value >= min
                    &&
                    value <= max
                );
            }
        );

    const sort =
        $("assetSort")
            ?.value
        || "id";

    records.sort(
        (
            a,
            b
        ) => {

            if (sort === "name") {
                return String(
                    a.name || ""
                ).localeCompare(
                    String(
                        b.name || ""
                    )
                );
            }

            if (sort === "value") {
                return Number(
                    b.current_value
                    || b.purchase_value
                    || 0
                )
                -
                Number(
                    a.current_value
                    || a.purchase_value
                    || 0
                );
            }

            if (sort === "status") {
                return String(
                    a.status || ""
                ).localeCompare(
                    String(
                        b.status || ""
                    )
                );
            }

            if (sort === "location") {
                return String(
                    a.location || ""
                ).localeCompare(
                    String(
                        b.location || ""
                    )
                );
            }

            return Number(
                a.id || 0
            )
            -
            Number(
                b.id || 0
            );
        }
    );

    const page =
        state.assetPage;

    const size =
        state.assetPageSize;

    const start =
        (
            page - 1
        ) * size;

    const pageRecords =
        records.slice(
            start,
            start + size
        );

    if (!pageRecords.length) {
        $("assetTable").innerHTML =
            emptyState(
                "No assets match the current filters."
            );

        $("assetPageInfo")
            .textContent =
            "Page 1";

        return;
    }

    $("assetTable").innerHTML = `
        <div class="table-scroll">

            <table>

                <thead>

                    <tr>
                        <th>ID</th>
                        <th>Asset</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Location</th>
                        <th>Owner</th>
                        <th>Value</th>
                        <th>Updated</th>
                        <th>Actions</th>
                    </tr>

                </thead>

                <tbody>

                    ${pageRecords.map(
                        asset => `
                            <tr>

                                <td>
                                    ${asset.id}
                                </td>

                                <td>
                                    <strong>
                                        ${escapeHtml(
                                            asset.asset_code
                                        )}
                                    </strong>

                                    <small>
                                        ${escapeHtml(
                                            asset.name
                                        )}
                                    </small>
                                </td>

                                <td>
                                    ${escapeHtml(
                                        asset.asset_type
                                        || "-"
                                    )}
                                </td>

                                <td>
                                    <span class="
                                        status-pill
                                        ${statusClass(
                                            asset.status
                                        )}
                                    ">
                                        ${escapeHtml(
                                            asset.status
                                            || "-"
                                        )}
                                    </span>
                                </td>

                                <td>
                                    ${escapeHtml(
                                        asset.location
                                        || "-"
                                    )}
                                </td>

                                <td>
                                    ${escapeHtml(
                                        asset.owner
                                        || "-"
                                    )}
                                </td>

                                <td>
                                    ${formatMoney(
                                        asset.current_value
                                        || asset.purchase_value
                                    )}
                                </td>

                                <td>
                                    ${formatDate(
                                        asset.updated_at
                                    )}
                                </td>

                                <td>

                                    <div class="table-actions">

                                        <button
                                            class="icon-button"
                                            onclick="viewAsset(${asset.id})"
                                            title="View"
                                        >
                                            ◉
                                        </button>

                                        <button
                                            class="icon-button"
                                            onclick="editAsset(${asset.id})"
                                            title="Edit"
                                        >
                                            ✎
                                        </button>

                                        <button
                                            class="icon-button danger"
                                            onclick="deleteAsset(${asset.id})"
                                            title="Delete"
                                        >
                                            ×
                                        </button>

                                    </div>

                                </td>

                            </tr>
                        `
                    ).join("")}

                </tbody>

            </table>

        </div>
    `;

    const totalPages =
        Math.max(
            1,
            Math.ceil(
                records.length
                /
                size
            )
        );

    $("assetPageInfo")
        .textContent =
        `Page ${page} / ${totalPages} | ${records.length} visible`;
}


function renderSources() {

    let sources =
        [...state.sources];

    const search =
        (
            $("sourceSearch")
                ?.value
            || ""
        ).toLowerCase();

    const enabled =
        $("sourceEnabledFilter")
            ?.value
        || "";

    const type =
        $("sourceTypeFilter")
            ?.value
        || "";

    sources =
        sources.filter(
            source => {

                const text =
                    [
                        source.id,
                        source.name,
                        source.url
                    ]
                    .join(" ")
                    .toLowerCase();

                return (
                    (
                        !search
                        ||
                        text.includes(
                            search
                        )
                    )
                    &&
                    (
                        !enabled
                        ||
                        String(
                            source.enabled !== false
                        )
                        === enabled
                    )
                    &&
                    (
                        !type
                        ||
                        source.type
                        === type
                    )
                );
            }
        );

    $("sourceCards").innerHTML =
        sources.length
        ? sources.map(
            source => `

                <div class="source-card">

                    <div class="source-card-top">

                        <div class="source-icon">
                            ◎
                        </div>

                        <span class="
                            status-pill
                            ${
                                source.enabled === false
                                ? "disabled"
                                : "active"
                            }
                        ">
                            ${
                                source.enabled === false
                                ? "DISABLED"
                                : "ENABLED"
                            }
                        </span>

                    </div>

                    <h3>
                        ${escapeHtml(
                            source.name
                            || source.id
                        )}
                    </h3>

                    <div class="source-id">
                        ${escapeHtml(
                            source.id
                            || ""
                        )}
                    </div>

                    <div class="source-url">
                        ${escapeHtml(
                            source.url
                            || ""
                        )}
                    </div>

                    <div class="source-meta">

                        <span>
                            TYPE:
                            ${escapeHtml(
                                source.type
                                || "HTTP"
                            )}
                        </span>

                        <span>
                            METHOD:
                            ${escapeHtml(
                                source.method
                                || "GET"
                            )}
                        </span>

                        <span>
                            EVERY
                            ${Number(
                                source.schedule_minutes
                                || 5
                            )}
                            MIN
                        </span>

                    </div>

                    <div class="source-actions">

                        <button
                            class="button small primary"
                            onclick="runSource('${encodeURIComponent(source.id)}')"
                        >
                            ▶ SYNC NOW
                        </button>

                        <button
                            class="button small"
                            onclick="viewSource('${encodeURIComponent(source.id)}')"
                        >
                            Details
                        </button>

                        <button
                            class="button small"
                            onclick="editSource('${encodeURIComponent(source.id)}')"
                        >
                            Edit
                        </button>

                        <button
                            class="button small danger-button"
                            onclick="deleteSource('${encodeURIComponent(source.id)}')"
                        >
                            Delete
                        </button>

                    </div>

                </div>

            `
        ).join("")
        : emptyState(
            "No connected sources found."
        );
}


function renderSync() {

    if (!state.syncs.length) {

        $("syncTable").innerHTML =
            emptyState(
                "No synchronization records yet."
            );

        $("syncStats").innerHTML =
            renderSyncStats();

        return;
    }

    $("syncStats").innerHTML =
        renderSyncStats();

    $("syncTable").innerHTML = `

        <div class="table-scroll">

            <table>

                <thead>

                    <tr>
                        <th>ID</th>
                        <th>Source</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Found</th>
                        <th>Created</th>
                        <th>Updated</th>
                        <th>Failed</th>
                        <th>Started</th>
                        <th>Completed</th>
                        <th>Message</th>
                    </tr>

                </thead>

                <tbody>

                    ${state.syncs
                        .slice()
                        .reverse()
                        .map(
                            sync => `
                                <tr>

                                    <td>
                                        ${sync.id ?? "-"}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            sync.source_name
                                            || "-"
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            sync.source_type
                                            || "-"
                                        )}
                                    </td>

                                    <td>
                                        <span class="
                                            status-pill
                                            ${statusClass(
                                                sync.status
                                            )}
                                        ">
                                            ${escapeHtml(
                                                sync.status
                                                || "-"
                                            )}
                                        </span>
                                    </td>

                                    <td>
                                        ${sync.records_found ?? 0}
                                    </td>

                                    <td>
                                        ${sync.records_created ?? 0}
                                    </td>

                                    <td>
                                        ${sync.records_updated ?? 0}
                                    </td>

                                    <td>
                                        ${sync.records_failed ?? 0}
                                    </td>

                                    <td>
                                        ${formatDate(
                                            sync.started_at
                                        )}
                                    </td>

                                    <td>
                                        ${formatDate(
                                            sync.completed_at
                                        )}
                                    </td>

                                    <td class="message-cell">
                                        ${escapeHtml(
                                            sync.message
                                            || "-"
                                        )}
                                    </td>

                                </tr>
                            `
                        ).join("")}

                </tbody>

            </table>

        </div>
    `;
}


function renderSyncStats() {

    const found =
        state.syncs.reduce(
            (
                a,
                b
            ) =>
                a +
                Number(
                    b.records_found
                    || 0
                ),
            0
        );

    const created =
        state.syncs.reduce(
            (
                a,
                b
            ) =>
                a +
                Number(
                    b.records_created
                    || 0
                ),
            0
        );

    const updated =
        state.syncs.reduce(
            (
                a,
                b
            ) =>
                a +
                Number(
                    b.records_updated
                    || 0
                ),
            0
        );

    const failed =
        state.syncs.reduce(
            (
                a,
                b
            ) =>
                a +
                Number(
                    b.records_failed
                    || 0
                ),
            0
        );

    return [
        ["OPERATIONS", state.syncs.length],
        ["RECORDS FOUND", found],
        ["CREATED", created],
        ["UPDATED", updated],
        ["FAILED", failed]
    ].map(
        item => `
            <div class="mini-kpi">
                <span>
                    ${item[0]}
                </span>

                <strong>
                    ${item[1]}
                </strong>
            </div>
        `
    ).join("");
}


function renderAudit() {

    let records =
        [...state.audits];

    const search =
        (
            $("auditSearch")
                ?.value
            || ""
        ).toLowerCase();

    const action =
        $("auditActionFilter")
            ?.value
        || "";

    records =
        records.filter(
            item => {

                const text =
                    [
                        item.asset_code,
                        item.description,
                        item.action
                    ]
                    .join(" ")
                    .toLowerCase();

                return (
                    (
                        !search
                        ||
                        text.includes(
                            search
                        )
                    )
                    &&
                    (
                        !action
                        ||
                        item.action
                        === action
                    )
                );
            }
        );

    if (!records.length) {

        $("auditTable").innerHTML =
            emptyState(
                "No audit events found."
            );

        return;
    }

    $("auditTable").innerHTML = `

        <div class="table-scroll">

            <table>

                <thead>

                    <tr>
                        <th>ID</th>
                        <th>Action</th>
                        <th>Asset</th>
                        <th>Entity</th>
                        <th>Description</th>
                        <th>Source</th>
                        <th>Time</th>
                    </tr>

                </thead>

                <tbody>

                    ${records.map(
                        item => `
                            <tr>

                                <td>
                                    ${item.id ?? "-"}
                                </td>

                                <td>
                                    <span class="
                                        status-pill
                                        ${statusClass(
                                            item.action
                                        )}
                                    ">
                                        ${escapeHtml(
                                            item.action
                                            || "-"
                                        )}
                                    </span>
                                </td>

                                <td>
                                    ${escapeHtml(
                                        item.asset_code
                                        || "-"
                                    )}
                                </td>

                                <td>
                                    ${escapeHtml(
                                        item.entity_type
                                        || "-"
                                    )}
                                </td>

                                <td class="message-cell">
                                    ${escapeHtml(
                                        item.description
                                        || "-"
                                    )}
                                </td>

                                <td>
                                    ${escapeHtml(
                                        item.source
                                        || "-"
                                    )}
                                </td>

                                <td>
                                    ${formatDate(
                                        item.created_at
                                    )}
                                </td>

                            </tr>
                        `
                    ).join("")}

                </tbody>

            </table>

        </div>
    `;
}


function renderHealth() {

    const sourceTotal =
        state.sources.length;

    const enabled =
        state.sources.filter(
            x =>
                x.enabled !== false
        ).length;

    const failed =
        state.syncs.filter(
            x =>
                String(
                    x.status || ""
                ).toLowerCase()
                === "failed"
        ).length;

    $("healthCards").innerHTML = `

        <div class="health-card good">
            <span>API</span>
            <strong>ONLINE</strong>
            <small>
                FastAPI backend
            </small>
        </div>

        <div class="health-card good">
            <span>DATABASE</span>
            <strong>
                ${escapeHtml(
                    $("databaseStatus")
                        .textContent
                )}
            </strong>
            <small>
                PostgreSQL
            </small>
        </div>

        <div class="health-card good">
            <span>AUTOMATION</span>
            <strong>
                ENABLED
            </strong>
            <small>
                Integration engine
            </small>
        </div>

        <div class="health-card ${
            state.scheduler?.running
            ? "good"
            : "warning"
        }">
            <span>SCHEDULER</span>
            <strong>
                ${
                    state.scheduler?.running
                    ? "RUNNING"
                    : "STOPPED"
                }
            </strong>
            <small>
                ${
                    state.scheduler?.jobs?.length
                    || 0
                }
                jobs
            </small>
        </div>

        <div class="health-card ${
            failed
            ? "warning"
            : "good"
        }">
            <span>SYNC FAILURES</span>
            <strong>
                ${failed}
            </strong>
            <small>
                Recorded failures
            </small>
        </div>

        <div class="health-card good">
            <span>SOURCES</span>
            <strong>
                ${enabled}/${sourceTotal}
            </strong>
            <small>
                Enabled sources
            </small>
        </div>
    `;


    $("schedulerDetails").innerHTML =
        state.scheduler
        ? `
            <div>
                <span>Running</span>
                <strong>
                    ${
                        state.scheduler.running
                        ? "YES"
                        : "NO"
                    }
                </strong>
            </div>

            ${
                (
                    state.scheduler.jobs
                    || []
                )
                .map(
                    job => `
                        <div>
                            <span>
                                Job
                            </span>

                            <strong>
                                ${escapeHtml(
                                    job.id
                                )}
                            </strong>
                        </div>

                        <div>
                            <span>
                                Next Run
                            </span>

                            <strong>
                                ${formatDate(
                                    job.next_run_time
                                )}
                            </strong>
                        </div>
                    `
                )
                .join("")
            }
        `
        : emptyState(
            "Scheduler information unavailable."
        );


    const changeEntries =
        Object.entries(
            state.changes || {}
        );

    $("changeDetails").innerHTML =
        changeEntries.length
        ? changeEntries
            .map(
                ([id, hash]) => `
                    <div>
                        <span>
                            ${escapeHtml(id)}
                        </span>

                        <strong class="hash">
                            ${escapeHtml(hash)}
                        </strong>
                    </div>
                `
            )
            .join("")
        : emptyState(
            "No change hashes recorded yet."
        );
}


function emptyState(
    message
) {
    return `
        <div class="empty-state">
            <div class="empty-icon">
                ◌
            </div>

            <strong>
                ${escapeHtml(message)}
            </strong>

            <small>
                ATUL is ready for operational data.
            </small>
        </div>
    `;
}


function renderError(
    id,
    message
) {
    const target =
        $(id);

    if (!target)
        return;

    target.innerHTML = `
        <div class="error-state">
            <strong>
                Connection Error
            </strong>

            <small>
                ${escapeHtml(message)}
            </small>

            <button
                class="button small"
                onclick="refreshAll(true)"
            >
                Retry
            </button>
        </div>
    `;
}


function statusClass(
    status
) {
    const value =
        String(
            status || ""
        ).toLowerCase();

    if (
        value.includes("fail")
        ||
        value.includes("error")
        ||
        value === "retired"
        ||
        value === "inactive"
    ) {
        return "failed";
    }

    if (
        value.includes("maint")
        ||
        value.includes("warning")
        ||
        value.includes("running")
    ) {
        return "warning";
    }

    return "active";
}


function formatDate(
    value
) {
    if (!value)
        return "-";

    const date =
        new Date(value);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return String(value);
    }

    return date.toLocaleString();
}


function formatMoney(
    value
) {
    if (
        value === null
        ||
        value === undefined
        ||
        value === ""
    ) {
        return "-";
    }

    const number =
        Number(value);

    if (
        Number.isNaN(number)
    ) {
        return String(value);
    }

    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 2
        }
    ).format(number);
}


function showAssetForm(
    asset = null
) {

    const edit =
        Boolean(asset);

    openModal(
        edit
            ? "Edit Asset"
            : "Add Asset",

        `
            <form
                id="assetForm"
                class="form-grid"
            >

                <label>
                    Asset Code
                    <input
                        name="asset_code"
                        required
                        value="${escapeHtml(
                            asset?.asset_code
                            || ""
                        )}"
                    >
                </label>

                <label>
                    Name
                    <input
                        name="name"
                        required
                        value="${escapeHtml(
                            asset?.name
                            || ""
                        )}"
                    >
                </label>

                <label>
                    Asset Type
                    <input
                        name="asset_type"
                        required
                        value="${escapeHtml(
                            asset?.asset_type
                            || ""
                        )}"
                    >
                </label>

                <label>
                    Serial Number
                    <input
                        name="serial_number"
                        value="${escapeHtml(
                            asset?.serial_number
                            || ""
                        )}"
                    >
                </label>

                <label>
                    Status
                    <select name="status">

                        <option value="active"
                            ${
                                asset?.status
                                === "active"
                                ? "selected"
                                : ""
                            }>
                            Active
                        </option>

                        <option value="maintenance"
                            ${
                                asset?.status
                                === "maintenance"
                                ? "selected"
                                : ""
                            }>
                            Maintenance
                        </option>

                        <option value="retired"
                            ${
                                asset?.status
                                === "retired"
                                ? "selected"
                                : ""
                            }>
                            Retired
                        </option>

                        <option value="inactive"
                            ${
                                asset?.status
                                === "inactive"
                                ? "selected"
                                : ""
                            }>
                            Inactive
                        </option>

                    </select>
                </label>

                <label>
                    Location
                    <input
                        name="location"
                        value="${escapeHtml(
                            asset?.location
                            || ""
                        )}"
                    >
                </label>

                <label>
                    Owner
                    <input
                        name="owner"
                        value="${escapeHtml(
                            asset?.owner
                            || ""
                        )}"
                    >
                </label>

                <label>
                    Purchase Value
                    <input
                        name="purchase_value"
                        type="number"
                        step="0.01"
                        value="${escapeHtml(
                            asset?.purchase_value
                            ?? ""
                        )}"
                    >
                </label>

                <label>
                    Current Value
                    <input
                        name="current_value"
                        type="number"
                        step="0.01"
                        value="${escapeHtml(
                            asset?.current_value
                            ?? ""
                        )}"
                    >
                </label>

                <label class="full">
                    Description
                    <textarea
                        name="description"
                    >${escapeHtml(
                        asset?.description
                        || ""
                    )}</textarea>
                </label>

            </form>
        `,

        `
            <button
                class="button"
                onclick="closeModal()"
            >
                Cancel
            </button>

            <button
                class="button primary"
                onclick="saveAsset(${asset?.id || "null"})"
            >
                ${
                    edit
                    ? "Save Changes"
                    : "Create Asset"
                }
            </button>
        `
    );
}


async function saveAsset(
    id
) {
    const form =
        $("assetForm");

    const data =
        Object.fromEntries(
            new FormData(form)
        );

    [
        "purchase_value",
        "current_value"
    ].forEach(
        field => {
            if (
                data[field] === ""
            ) {
                data[field] = null;
            } else {
                data[field] =
                    Number(
                        data[field]
                    );
            }
        }
    );

    try {

        await api(
            id
            ? `/api/v1/assets/${id}`
            : "/api/v1/assets",
            {
                method:
                    id
                    ? "PUT"
                    : "POST",

                body:
                    JSON.stringify(
                        data
                    )
            }
        );

        closeModal();

        showToast(
            id
            ? "Asset updated."
            : "Asset created.",
            "success"
        );

        await refreshAll();

    } catch (error) {

        showToast(
            error.message,
            "error"
        );
    }
}


function addAsset() {
    showAssetForm();
}


function viewAsset(
    id
) {
    const asset =
        state.assets.find(
            x =>
                Number(x.id)
                === Number(id)
        );

    if (!asset)
        return;

    openModal(
        "Asset Details",

        `
            <div class="detail-grid">

                <div>
                    <span>ID</span>
                    <strong>
                        ${asset.id}
                    </strong>
                </div>

                <div>
                    <span>Asset Code</span>
                    <strong>
                        ${escapeHtml(
                            asset.asset_code
                        )}
                    </strong>
                </div>

                <div>
                    <span>Name</span>
                    <strong>
                        ${escapeHtml(
                            asset.name
                        )}
                    </strong>
                </div>

                <div>
                    <span>Type</span>
                    <strong>
                        ${escapeHtml(
                            asset.asset_type
                        )}
                    </strong>
                </div>

                <div>
                    <span>Serial</span>
                    <strong>
                        ${escapeHtml(
                            asset.serial_number
                            || "-"
                        )}
                    </strong>
                </div>

                <div>
                    <span>Status</span>
                    <strong>
                        ${escapeHtml(
                            asset.status
                            || "-"
                        )}
                    </strong>
                </div>

                <div>
                    <span>Location</span>
                    <strong>
                        ${escapeHtml(
                            asset.location
                            || "-"
                        )}
                    </strong>
                </div>

                <div>
                    <span>Owner</span>
                    <strong>
                        ${escapeHtml(
                            asset.owner
                            || "-"
                        )}
                    </strong>
                </div>

                <div>
                    <span>Purchase Value</span>
                    <strong>
                        ${formatMoney(
                            asset.purchase_value
                        )}
                    </strong>
                </div>

                <div>
                    <span>Current Value</span>
                    <strong>
                        ${formatMoney(
                            asset.current_value
                        )}
                    </strong>
                </div>

                <div class="full">
                    <span>Description</span>
                    <strong>
                        ${escapeHtml(
                            asset.description
                            || "-"
                        )}
                    </strong>
                </div>

                <div class="full">
                    <span>Metadata</span>
                    <pre>${escapeHtml(
                        JSON.stringify(
                            asset.asset_metadata
                            || {},
                            null,
                            2
                        )
                    )}</pre>
                </div>

            </div>
        `,

        `
            <button
                class="button"
                onclick="closeModal()"
            >
                Close
            </button>

            <button
                class="button primary"
                onclick="editAsset(${asset.id})"
            >
                Edit
            </button>
        `
    );
}


function editAsset(
    id
) {
    const asset =
        state.assets.find(
            x =>
                Number(x.id)
                === Number(id)
        );

    if (!asset)
        return;

    showAssetForm(
        asset
    );
}


async function deleteAsset(
    id
) {

    const asset =
        state.assets.find(
            x =>
                Number(x.id)
                === Number(id)
        );

    if (!asset)
        return;

    const confirmed =
        confirm(
            `Delete asset ${asset.asset_code}?`
        );

    if (!confirmed)
        return;

    try {

        await api(
            `/api/v1/assets/${id}`,
            {
                method: "DELETE"
            }
        );

        showToast(
            "Asset deleted.",
            "success"
        );

        await refreshAll();

    } catch (error) {

        showToast(
            error.message,
            "error"
        );
    }
}


function showSourceForm(
    source = null
) {

    const edit =
        Boolean(source);

    openModal(
        edit
            ? "Edit Source"
            : "Add Source",

        `
            <form
                id="sourceForm"
                class="form-grid"
            >

                ${
                    edit
                    ? `
                        <label>
                            Source ID
                            <input
                                name="id"
                                readonly
                                value="${escapeHtml(
                                    source.id
                                )}"
                            >
                        </label>
                    `
                    : `
                        <label>
                            Source ID
                            <input
                                name="id"
                                required
                                placeholder="my-api-source"
                            >
                        </label>
                    `
                }

                <label>
                    Name
                    <input
                        name="name"
                        required
                        value="${escapeHtml(
                            source?.name
                            || ""
                        )}"
                    >
                </label>

                <label class="full">
                    URL
                    <input
                        name="url"
                        required
                        type="url"
                        value="${escapeHtml(
                            source?.url
                            || ""
                        )}"
                    >
                </label>

                <label>
                    Type
                    <select name="type">

                        <option value="http_json">
                            HTTP JSON
                        </option>

                        <option value="http">
                            HTTP
                        </option>

                        <option value="website">
                            Website
                        </option>

                    </select>
                </label>

                <label>
                    Method
                    <select name="method">

                        <option value="GET">
                            GET
                        </option>

                        <option value="POST">
                            POST
                        </option>

                    </select>
                </label>

                <label>
                    Timeout
                    <input
                        name="timeout"
                        type="number"
                        min="1"
                        value="${escapeHtml(
                            source?.timeout
                            || 30
                        )}"
                    >
                </label>

                <label>
                    Schedule Minutes
                    <input
                        name="schedule_minutes"
                        type="number"
                        min="1"
                        value="${escapeHtml(
                            source?.schedule_minutes
                            || 5
                        )}"
                    >
                </label>

                <label>
                    Enabled
                    <select name="enabled">

                        <option value="true"
                            ${
                                source?.enabled !== false
                                ? "selected"
                                : ""
                            }>
                            Enabled
                        </option>

                        <option value="false"
                            ${
                                source?.enabled === false
                                ? "selected"
                                : ""
                            }>
                            Disabled
                        </option>

                    </select>
                </label>

                <label class="full">
                    Asset Mapping JSON
                    <textarea
                        name="asset_mapping"
                        placeholder='{"asset_code":"id","name":"title"}'
                    >${escapeHtml(
                        JSON.stringify(
                            source?.asset_mapping
                            || {
                                asset_code:
                                    "id",
                                name:
                                    "title",
                                description:
                                    "body"
                            },
                            null,
                            2
                        )
                    )}</textarea>
                </label>

            </form>
        `,

        `
            <button
                class="button"
                onclick="closeModal()"
            >
                Cancel
            </button>

            <button
                class="button primary"
                onclick="saveSource(${edit ? "true" : "false"})"
            >
                ${
                    edit
                    ? "Save Changes"
                    : "Create Source"
                }
            </button>
        `
    );
}


async function saveSource(
    editing
) {

    const form =
        $("sourceForm");

    const raw =
        Object.fromEntries(
            new FormData(form)
        );

    let mapping = {};

    try {
        mapping =
            raw.asset_mapping
            ? JSON.parse(
                raw.asset_mapping
            )
            : {};
    } catch {

        showToast(
            "Asset mapping JSON is invalid.",
            "error"
        );

        return;
    }

    const data = {
        ...raw,
        type:
            raw.type
            || "http_json",

        method:
            raw.method
            || "GET",

        timeout:
            Number(
                raw.timeout
                || 30
            ),

        schedule_minutes:
            Number(
                raw.schedule_minutes
                || 5
            ),

        enabled:
            raw.enabled
            === "true",

        headers: {},
        params: {},

        asset_mapping:
            mapping
    };

    delete data.asset_mapping_raw;

    try {

        if (editing) {

            const id =
                raw.id;

            delete data.id;

            await api(
                `/api/v1/automation/sources/${encodeURIComponent(id)}`,
                {
                    method: "PUT",
                    body:
                        JSON.stringify(
                            data
                        )
                }
            );

        } else {

            await api(
                "/api/v1/automation/sources",
                {
                    method: "POST",
                    body:
                        JSON.stringify(
                            data
                        )
                }
            );
        }

        closeModal();

        showToast(
            editing
            ? "Source updated."
            : "Source created.",
            "success"
        );

        await refreshAll();

    } catch (error) {

        showToast(
            error.message,
            "error"
        );
    }
}


function addSource() {
    showSourceForm();
}


function getSource(
    encodedId
) {
    const id =
        decodeURIComponent(
            encodedId
        );

    return state.sources.find(
        x =>
            x.id === id
    );
}


function viewSource(
    encodedId
) {

    const source =
        getSource(
            encodedId
        );

    if (!source)
        return;

    const hash =
        state.changes[
            source.id
        ];

    openModal(
        "Source Details",

        `
            <div class="detail-grid">

                <div>
                    <span>ID</span>
                    <strong>
                        ${escapeHtml(
                            source.id
                        )}
                    </strong>
                </div>

                <div>
                    <span>Name</span>
                    <strong>
                        ${escapeHtml(
                            source.name
                        )}
                    </strong>
                </div>

                <div class="full">
                    <span>URL</span>
                    <strong>
                        ${escapeHtml(
                            source.url
                        )}
                    </strong>
                </div>

                <div>
                    <span>Type</span>
                    <strong>
                        ${escapeHtml(
                            source.type
                        )}
                    </strong>
                </div>

                <div>
                    <span>Method</span>
                    <strong>
                        ${escapeHtml(
                            source.method
                        )}
                    </strong>
                </div>

                <div>
                    <span>Timeout</span>
                    <strong>
                        ${source.timeout || 30}s
                    </strong>
                </div>

                <div>
                    <span>Schedule</span>
                    <strong>
                        Every
                        ${source.schedule_minutes || 5}
                        minutes
                    </strong>
                </div>

                <div>
                    <span>Enabled</span>
                    <strong>
                        ${
                            source.enabled !== false
                            ? "YES"
                            : "NO"
                        }
                    </strong>
                </div>

                <div class="full">
                    <span>SHA256</span>
                    <strong class="hash">
                        ${escapeHtml(
                            hash || "Not synchronized yet"
                        )}
                    </strong>
                </div>

                <div class="full">
                    <span>Asset Mapping</span>
                    <pre>${escapeHtml(
                        JSON.stringify(
                            source.asset_mapping
                            || {},
                            null,
                            2
                        )
                    )}</pre>
                </div>

            </div>
        `,

        `
            <button
                class="button"
                onclick="closeModal()"
            >
                Close
            </button>

            <button
                class="button primary"
                onclick="runSource('${encodeURIComponent(source.id)}')"
            >
                ▶ Sync Now
            </button>
        `
    );
}


function editSource(
    encodedId
) {

    const source =
        getSource(
            encodedId
        );

    if (!source)
        return;

    showSourceForm(
        source
    );
}


async function deleteSource(
    encodedId
) {

    const source =
        getSource(
            encodedId
        );

    if (!source)
        return;

    const confirmed =
        confirm(
            `Delete source "${source.name}"?`
        );

    if (!confirmed)
        return;

    try {

        await api(
            `/api/v1/automation/sources/${encodeURIComponent(source.id)}`,
            {
                method: "DELETE"
            }
        );

        showToast(
            "Source deleted.",
            "success"
        );

        await refreshAll();

    } catch (error) {

        showToast(
            error.message,
            "error"
        );
    }
}


async function runSource(
    encodedId
) {

    const id =
        decodeURIComponent(
            encodedId
        );

    closeModal();

    showToast(
        "Synchronization started...",
        "info"
    );

    try {

        const result =
            await api(
                `/api/v1/automation/run/${encodeURIComponent(id)}`,
                {
                    method: "POST"
                }
            );

        if (
            result.success
        ) {
            showToast(
                `Synchronization completed. Created: ${result.records_created || 0}, Updated: ${result.records_updated || 0}.`,
                "success"
            );
        } else {
            showToast(
                result.error
                || "Synchronization failed.",
                "error"
            );
        }

        await refreshAll();

    } catch (error) {

        showToast(
            error.message,
            "error"
        );
    }
}


async function runAllSources() {

    showToast(
        "Global synchronization started...",
        "info"
    );

    try {

        const result =
            await api(
                "/api/v1/automation/run",
                {
                    method: "POST"
                }
            );

        const results =
            result.results || [];

        const successful =
            results.filter(
                x =>
                    x.success
            ).length;

        showToast(
            `Synchronization finished. ${successful}/${results.length} sources completed.`,
            "success"
        );

        await refreshAll();

    } catch (error) {

        showToast(
            error.message,
            "error"
        );
    }
}


function navigate(
    view
) {

    document
        .querySelectorAll(".nav-item")
        .forEach(
            button => {
                button.classList.toggle(
                    "active",
                    button.dataset.view
                    === view
                );
            }
        );

    document
        .querySelectorAll(".view")
        .forEach(
            section => {
                section.classList.toggle(
                    "active-view",
                    section.id
                    === `view-${view}`
                );
            }
        );

    state.currentView =
        view;

    const titles = {
        dashboard:
            "Command Center",
        assets:
            "Asset Registry",
        sources:
            "Integration Network",
        sync:
            "Synchronization Center",
        audit:
            "Audit Center",
        health:
            "System Health",
        settings:
            "Platform Settings"
    };

    $("pageTitle")
        .textContent =
        titles[view]
        || "Command Center";

    if (
        window.innerWidth < 900
    ) {
        document
            .querySelector(".sidebar")
            ?.classList
            .remove("mobile-open");
    }

    if (
        view === "assets"
    ) {
        loadAssets();
    }

    if (
        view === "sources"
    ) {
        loadSources();
    }

    if (
        view === "sync"
    ) {
        loadSyncs();
    }

    if (
        view === "audit"
    ) {
        loadAudits();
    }

    if (
        view === "health"
    ) {
        loadScheduler();
        loadChanges();
    }
}


function setupNavigation() {

    document
        .querySelectorAll(
            ".nav-item"
        )
        .forEach(
            button => {
                button.addEventListener(
                    "click",
                    () =>
                        navigate(
                            button.dataset.view
                        )
                );
            }
        );

    document
        .querySelectorAll(
            "[data-view-button]"
        )
        .forEach(
            button => {
                button.addEventListener(
                    "click",
                    () =>
                        navigate(
                            button.dataset.viewButton
                        )
                );
            }
        );
}


function setupFilters() {

    [
        "assetSearch",
        "assetStatusFilter",
        "assetTypeFilter",
        "locationFilter",
        "ownerFilter",
        "minValueFilter",
        "maxValueFilter",
        "assetSort"
    ].forEach(
        id => {

            const element =
                $(id);

            if (!element)
                return;

            element.addEventListener(
                "input",
                () => {
                    state.assetPage = 1;
                    renderAssets();
                }
            );

            element.addEventListener(
                "change",
                () => {
                    state.assetPage = 1;
                    renderAssets();
                }
            );
        }
    );


    [
        "sourceSearch",
        "sourceEnabledFilter",
        "sourceTypeFilter"
    ].forEach(
        id => {

            const element =
                $(id);

            if (!element)
                return;

            element.addEventListener(
                "input",
                renderSources
            );

            element.addEventListener(
                "change",
                renderSources
            );
        }
    );


    [
        "auditSearch",
        "auditActionFilter"
    ].forEach(
        id => {

            const element =
                $(id);

            if (!element)
                return;

            element.addEventListener(
                "input",
                renderAudit
            );

            element.addEventListener(
                "change",
                renderAudit
            );
        }
    );


    $("resetAssetFilters")
        .addEventListener(
            "click",
            () => {

                [
                    "assetSearch",
                    "assetTypeFilter",
                    "locationFilter",
                    "ownerFilter",
                    "minValueFilter",
                    "maxValueFilter"
                ].forEach(
                    id => {
                        $(id).value =
                            "";
                    }
                );

                $("assetStatusFilter")
                    .value = "";

                state.assetPage =
                    1;

                loadAssets();
            }
        );
}


function setupPagination() {

    $("assetPrev")
        .addEventListener(
            "click",
            () => {

                if (
                    state.assetPage
                    > 1
                ) {
                    state.assetPage--;
                    loadAssets();
                }
            }
        );

    $("assetNext")
        .addEventListener(
            "click",
            () => {

                state.assetPage++;
                loadAssets();
            }
        );

    $("assetPageSize")
        .addEventListener(
            "change",
            event => {

                state.assetPageSize =
                    Number(
                        event.target.value
                    );

                state.assetPage =
                    1;

                loadAssets();
            }
        );
}


function setupButtons() {

    $("refreshBtn")
        .addEventListener(
            "click",
            () =>
                refreshAll(true)
        );

    $("runAllBtn")
        .addEventListener(
            "click",
            runAllSources
        );

    $("addAssetBtn")
        .addEventListener(
            "click",
            addAsset
        );

    $("assetsAddBtn")
        .addEventListener(
            "click",
            addAsset
        );

    $("addSourceBtn")
        .addEventListener(
            "click",
            addSource
        );

    $("sourcesAddBtn")
        .addEventListener(
            "click",
            addSource
        );

    $("refreshSourcesBtn")
        .addEventListener(
            "click",
            () =>
                loadSources()
        );

    $("syncNowPageBtn")
        .addEventListener(
            "click",
            runAllSources
        );

    $("healthRefreshBtn")
        .addEventListener(
            "click",
            () => {
                loadScheduler();
                loadChanges();
                showToast(
                    "Health information refreshed.",
                    "success"
                );
            }
        );

    $("modalClose")
        .addEventListener(
            "click",
            closeModal
        );

    $("modalBackdrop")
        .addEventListener(
            "click",
            event => {
                if (
                    event.target
                    ===
                    $("modalBackdrop")
                ) {
                    closeModal();
                }
            }
        );

    $("mobileMenu")
        .addEventListener(
            "click",
            () =>
                document
                    .querySelector(
                        ".sidebar"
                    )
                    .classList
                    .toggle(
                        "mobile-open"
                    )
        );
}


function setupGlobalSearch() {

    $("globalSearch")
        .addEventListener(
            "input",
            event => {

                const query =
                    event.target.value
                        .trim()
                        .toLowerCase();

                if (!query)
                    return;

                const assetMatch =
                    (
                        state.analyticsAssets
                        || []
                    ).find(
                        asset =>
                            [
                                asset.asset_code,
                                asset.name,
                                asset.serial_number,
                                asset.owner,
                                asset.location
                            ]
                            .join(" ")
                            .toLowerCase()
                            .includes(
                                query
                            )
                    );

                const sourceMatch =
                    state.sources.find(
                        source =>
                            [
                                source.id,
                                source.name,
                                source.url
                            ]
                            .join(" ")
                            .toLowerCase()
                            .includes(
                                query
                            )
                    );

                if (
                    assetMatch
                ) {

                    navigate(
                        "assets"
                    );

                    $("assetSearch")
                        .value =
                        query;

                    renderAssets();

                    return;
                }

                if (
                    sourceMatch
                ) {

                    navigate(
                        "sources"
                    );

                    $("sourceSearch")
                        .value =
                        query;

                    renderSources();
                }
            }
        );
}


function setupKeyboard() {

    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key
                ===
                "Escape"
            ) {
                closeModal();
            }

            if (
                event.ctrlKey
                &&
                event.key.toLowerCase()
                === "k"
            ) {

                event.preventDefault();

                $("globalSearch")
                    .focus();
            }

            if (
                event.ctrlKey
                &&
                event.key.toLowerCase()
                === "r"
            ) {

                event.preventDefault();

                refreshAll(true);
            }
        }
    );
}


function setupExports() {

    $("exportJsonBtn")
        .addEventListener(
            "click",
            () => {

                downloadFile(
                    "atul-assets.json",
                    JSON.stringify(
                        state.analyticsAssets
                        || state.assets,
                        null,
                        2
                    ),
                    "application/json"
                );

                showToast(
                    "JSON export created.",
                    "success"
                );
            }
        );


    $("exportCsvBtn")
        .addEventListener(
            "click",
            () => {

                const assets =
                    state.analyticsAssets
                    || state.assets;

                const fields = [
                    "id",
                    "asset_code",
                    "name",
                    "asset_type",
                    "serial_number",
                    "status",
                    "location",
                    "owner",
                    "purchase_value",
                    "current_value",
                    "description",
                    "created_at",
                    "updated_at"
                ];

                const csv = [
                    fields.join(","),
                    ...assets.map(
                        asset =>
                            fields.map(
                                field =>
                                    csvValue(
                                        asset[field]
                                    )
                            ).join(",")
                    )
                ].join("\n");

                downloadFile(
                    "atul-assets.csv",
                    csv,
                    "text/csv"
                );

                showToast(
                    "CSV export created.",
                    "success"
                );
            }
        );


    $("printAssetsBtn")
        .addEventListener(
            "click",
            () =>
                window.print()
        );


    $("importCsvBtn")
        .addEventListener(
            "click",
            () =>
                $("csvInput").click()
        );


    $("csvInput")
        .addEventListener(
            "change",
            event => {

                const file =
                    event.target.files[0];

                if (!file)
                    return;

                const reader =
                    new FileReader();

                reader.onload =
                    () =>
                        importCsv(
                            reader.result
                        );

                reader.readAsText(
                    file
                );
            }
        );
}


async function importCsv(
    text
) {

    const lines =
        text
            .split(/\r?\n/)
            .filter(
                line =>
                    line.trim()
            );

    if (
        lines.length < 2
    ) {

        showToast(
            "CSV contains no records.",
            "error"
        );

        return;
    }

    const headers =
        parseCsvLine(
            lines[0]
        );

    let created =
        0;

    let failed =
        0;

    for (
        const line
        of lines.slice(1)
    ) {

        const values =
            parseCsvLine(
                line
            );

        const record = {};

        headers.forEach(
            (
                header,
                index
            ) => {
                record[header] =
                    values[index]
                    || "";
            }
        );

        try {

            if (
                !record.asset_code
                ||
                !record.name
                ||
                !record.asset_type
            ) {
                failed++;
                return;
            }

            await api(
                "/api/v1/assets",
                {
                    method: "POST",
                    body:
                        JSON.stringify(
                            {
                                ...record,
                                purchase_value:
                                    record.purchase_value
                                    ? Number(
                                        record.purchase_value
                                    )
                                    : null,
                                current_value:
                                    record.current_value
                                    ? Number(
                                        record.current_value
                                    )
                                    : null
                            }
                        )
                }
            );

            created++;

        } catch {

            failed++;
        }
    }

    showToast(
        `CSV import completed. Created: ${created}, Failed: ${failed}.`,
        failed
        ? "warning"
        : "success"
    );

    await refreshAll();
}


function parseCsvLine(
    line
) {
    const result = [];
    let current = "";
    let quoted = false;

    for (
        let i = 0;
        i < line.length;
        i++
    ) {

        const char =
            line[i];

        if (
            char === '"'
        ) {

            if (
                quoted
                &&
                line[i + 1]
                === '"'
            ) {

                current += '"';
                i++;

            } else {

                quoted =
                    !quoted;
            }

        } else if (
            char === ","
            &&
            !quoted
        ) {

            result.push(
                current
            );

            current = "";

        } else {

            current +=
                char;
        }
    }

    result.push(
        current
    );

    return result;
}


function csvValue(
    value
) {
    const string =
        value === null
        ||
        value === undefined
        ? ""
        : String(value);

    return `"${string.replaceAll(
        '"',
        '""'
    )}"`;
}


function downloadFile(
    filename,
    content,
    type
) {
    const blob =
        new Blob(
            [content],
            {type}
        );

    const url =
        URL.createObjectURL(
            blob
        );

    const anchor =
        document.createElement(
            "a"
        );

    anchor.href =
        url;

    anchor.download =
        filename;

    anchor.click();

    URL.revokeObjectURL(
        url
    );
}


function setupSettings() {

    $("backendUrlInput")
        .value =
        state.backendUrl;

    $("saveBackendUrl")
        .addEventListener(
            "click",
            () => {

                const value =
                    $("backendUrlInput")
                        .value
                        .trim()
                        .replace(
                            /\/$/,
                            ""
                        );

                if (!value) {
                    showToast(
                        "Backend URL is required.",
                        "error"
                    );

                    return;
                }

                state.backendUrl =
                    value;

                localStorage.setItem(
                    "atul_backend_url",
                    value
                );

                showToast(
                    "Backend URL saved.",
                    "success"
                );

                refreshAll();
            }
        );


    $("applyRefresh")
        .addEventListener(
            "click",
            () => {

                const value =
                    Number(
                        $("refreshInterval")
                            .value
                    );

                setRefreshInterval(
                    value
                );

                showToast(
                    value
                    ? `Automatic refresh set to ${value / 1000} seconds.`
                    : "Automatic refresh disabled.",
                    "success"
                );
            }
        );
}


function setRefreshInterval(
    milliseconds
) {

    if (
        state.refreshTimer
    ) {
        clearInterval(
            state.refreshTimer
        );

        state.refreshTimer =
            null;
    }

    state.refreshSeconds =
        milliseconds
        ? milliseconds / 1000
        : 0;

    if (
        milliseconds
    ) {

        state.refreshTimer =
            setInterval(
                () => {

                    if (
                        !state.refreshPaused
                    ) {
                        refreshAll();
                    }

                },
                milliseconds
            );
    }
}


function initialize() {

    setupNavigation();
    setupFilters();
    setupPagination();
    setupButtons();
    setupGlobalSearch();
    setupKeyboard();
    setupExports();
    setupSettings();

    setRefreshInterval(
        30000
    );

    refreshAll();

    window.addEventListener(
        "online",
        () => {

            showToast(
                "Browser connection restored.",
                "success"
            );

            refreshAll();
        }
    );

    window.addEventListener(
        "offline",
        () => {

            showToast(
                "Browser connection lost.",
                "error"
            );
        }
    );
}


window.addAsset =
    addAsset;

window.viewAsset =
    viewAsset;

window.editAsset =
    editAsset;

window.deleteAsset =
    deleteAsset;

window.addSource =
    addSource;

window.viewSource =
    viewSource;

window.editSource =
    editSource;

window.deleteSource =
    deleteSource;

window.runSource =
    runSource;

window.closeModal =
    closeModal;

window.refreshAll =
    refreshAll;

window.saveAsset =
    saveAsset;

window.saveSource =
    saveSource;


document.addEventListener(
    "DOMContentLoaded",
    initialize
);
