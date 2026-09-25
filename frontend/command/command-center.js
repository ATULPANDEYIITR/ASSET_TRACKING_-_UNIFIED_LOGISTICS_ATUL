const API = "http://127.0.0.1:8000/api/v1";

let dashboardData = {};
let assets = [];
let sources = [];
let syncRecords = [];
let auditRecords = [];

const $ = id => document.getElementById(id);

function escapeHTML(value) {
    if (value === null || value === undefined) return "";
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function formatNumber(value) {
    return Number(value || 0).toLocaleString("en-IN");
}

function formatMoney(value) {
    return Number(value || 0).toLocaleString(
        "en-IN",
        {
            maximumFractionDigits: 2
        }
    );
}

function formatTime(value) {
    if (!value) return "--";
    const d = new Date(value);
    return d.toLocaleString();
}

function notify(message, type = "normal") {

    const box = $("notification");

    box.textContent = message;

    box.className = "notification visible " + type;

    setTimeout(() => {
        box.className = "notification";
    }, 3500);
}

async function getJSON(url, options = {}) {

    const response = await fetch(url, options);

    if (!response.ok) {
        throw new Error(
            `${response.status} ${response.statusText}`
        );
    }

    return await response.json();
}

async function loadDashboard() {

    try {

        dashboardData =
            await getJSON(
                `${API}/intelligence/dashboard`
            );

        renderDashboard();

    } catch (error) {

        notify(
            "Dashboard data unavailable: " + error.message,
            "error"
        );

    }
}

async function loadAssets() {

    try {

        const data =
            await getJSON(
                `${API}/assets?page=1&page_size=500`
            );

        assets =
            data.assets ||
            data.items ||
            data ||
            [];

        renderAssets();

    } catch (error) {

        notify(
            "Asset data unavailable",
            "error"
        );

    }
}

async function loadSources() {

    try {

        const data =
            await getJSON(
                `${API}/automation/sources`
            );

        sources =
            data.sources ||
            data.items ||
            data ||
            [];

        renderSources();

    } catch (error) {

        notify(
            "Source registry unavailable",
            "error"
        );

    }
}

async function loadSync() {

    try {

        const data =
            await getJSON(
                `${API}/synchronization`
            );

        syncRecords =
            data.sync_records ||
            data.records ||
            data.items ||
            data ||
            [];

        if (!Array.isArray(syncRecords)) {
            syncRecords = [];
        }

        renderSync();

    } catch (error) {

        notify(
            "Synchronization history unavailable",
            "error"
        );

    }
}

async function loadAudit() {

    try {

        const data =
            await getJSON(
                `${API}/audit?limit=500`
            );

        auditRecords =
            data.audit_records ||
            data.records ||
            data.items ||
            data ||
            [];

        if (!Array.isArray(auditRecords)) {
            auditRecords = [];
        }

        renderAudit();

    } catch (error) {

        notify(
            "Audit history unavailable",
            "error"
        );

    }
}

async function loadHealth() {

    try {

        const data =
            await getJSON(
                `${API}/intelligence/health`
            );

        $("healthApi").textContent = "ONLINE";
        $("healthDatabase").textContent =
            String(data.database || "unknown").toUpperCase();

        $("healthAssets").textContent =
            formatNumber(data.assets);

        $("healthAudit").textContent =
            formatNumber(data.audit_records);

        $("healthSync").textContent =
            formatNumber(data.sync_records);

        $("healthTime").textContent =
            formatTime(data.checked_at);

    } catch (error) {

        $("healthApi").textContent = "OFFLINE";
        $("healthDatabase").textContent = "ERROR";

        notify(
            "Health check failed",
            "error"
        );

    }
}

function renderDashboard() {

    const a = dashboardData.assets || {};
    const f = dashboardData.financial || {};
    const s = dashboardData.synchronization || {};
    const audit = dashboardData.audit || {};

    $("totalAssets").textContent =
        formatNumber(a.total);

    $("activeAssets").textContent =
        formatNumber(a.active);

    $("maintenanceAssets").textContent =
        formatNumber(a.maintenance);

    $("locationCount").textContent =
        formatNumber(a.locations);

    $("ownerCount").textContent =
        formatNumber(a.owners);

    $("typeCount").textContent =
        formatNumber(a.types);

    $("syncCount").textContent =
        formatNumber(s.total);

    $("auditCount").textContent =
        formatNumber(audit.total);

    $("purchaseValue").textContent =
        "₹ " + formatMoney(f.purchase_value);

    $("currentValue").textContent =
        "₹ " + formatMoney(f.current_value);

    $("valueChange").textContent =
        "₹ " + formatMoney(f.value_change);

    $("depreciation").textContent =
        "₹ " + formatMoney(f.depreciation);

    $("syncSuccess").textContent =
        formatNumber(s.successful);

    $("syncFailed").textContent =
        formatNumber(s.failed);

    const totalSync =
        Number(s.successful || 0) +
        Number(s.failed || 0);

    const successPercent =
        totalSync
            ? Math.round(
                Number(s.successful || 0)
                / totalSync * 100
            )
            : 0;

    const failedPercent =
        totalSync
            ? Math.round(
                Number(s.failed || 0)
                / totalSync * 100
            )
            : 0;

    $("syncSuccessBar").style.width =
        successPercent + "%";

    $("syncFailedBar").style.width =
        failedPercent + "%";

    $("lastUpdated").textContent =
        "Updated " +
        formatTime(dashboardData.generated_at);

    renderActivity();
}

function renderActivity() {

    const container =
        $("activityTimeline");

    const events =
        dashboardData.recent_audit || [];

    if (!events.length) {

        container.innerHTML =
            '<div class="empty">No audit activity recorded yet.</div>';

        return;
    }

    container.innerHTML =
        events.map(event => {

            return `
                <div class="timeline-item">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <strong>
                            ${escapeHTML(event.action)}
                        </strong>
                        <span>
                            ${escapeHTML(event.description || "System event")}
                        </span>
                        <small>
                            ${escapeHTML(event.asset_code || "")}
                            ·
                            ${escapeHTML(event.source || "")}
                            ·
                            ${escapeHTML(formatTime(event.created_at))}
                        </small>
                    </div>
                </div>
            `;

        }).join("");
}

function renderAssets() {

    const query =
        ($("assetSearch").value || "")
            .trim()
            .toLowerCase();

    const filtered =
        assets.filter(asset => {

            const text = [
                asset.asset_code,
                asset.name,
                asset.asset_type,
                asset.status,
                asset.location,
                asset.owner
            ]
            .join(" ")
            .toLowerCase();

            return text.includes(query);
        });

    $("visibleAssets").textContent =
        formatNumber(filtered.length);

    $("assetActiveMini").textContent =
        formatNumber(
            filtered.filter(
                x => x.status === "active"
            ).length
        );

    $("assetMaintenanceMini").textContent =
        formatNumber(
            filtered.filter(
                x => x.status === "maintenance"
            ).length
        );

    $("assetTable").innerHTML =
        filtered.map(asset => {

            return `
                <tr>
                    <td>${escapeHTML(asset.id)}</td>
                    <td class="code">
                        ${escapeHTML(asset.asset_code)}
                    </td>
                    <td>
                        ${escapeHTML(asset.name)}
                    </td>
                    <td>
                        ${escapeHTML(asset.asset_type)}
                    </td>
                    <td>
                        <span class="status ${escapeHTML(asset.status)}">
                            ${escapeHTML(asset.status)}
                        </span>
                    </td>
                    <td>
                        ${escapeHTML(asset.location)}
                    </td>
                    <td>
                        ${escapeHTML(asset.owner)}
                    </td>
                    <td>
                        ₹ ${formatMoney(asset.current_value)}
                    </td>
                </tr>
            `;

        }).join("");

    if (!filtered.length) {

        $("assetTable").innerHTML =
            `<tr>
                <td colspan="8" class="empty">
                    No matching assets found.
                </td>
            </tr>`;
    }
}

function getSourceLatestSync(source) {

    const name =
        String(source.name || source.id || "")
            .toLowerCase();

    return syncRecords.find(record => {

        const sourceName =
            String(record.source_name || "")
                .toLowerCase();

        return sourceName === name;

    });
}

function sourceStatus(source) {

    const latest =
        getSourceLatestSync(source);

    if (!latest) {

        return {
            label: "NOT TESTED",
            className: "unknown"
        };
    }

    const status =
        String(latest.status || "")
            .toLowerCase();

    if (
        status === "completed" ||
        status === "success" ||
        status === "successful"
    ) {

        return {
            label: "ONLINE",
            className: "online"
        };
    }

    if (
        status === "failed" ||
        status === "error"
    ) {

        return {
            label: "OFFLINE",
            className: "offline"
        };
    }

    if (status === "running") {

        return {
            label: "SYNCING",
            className: "syncing"
        };
    }

    return {
        label: status.toUpperCase(),
        className: "unknown"
    };
}

function renderSources() {

    $("sourceTotal").textContent =
        formatNumber(sources.length);

    const enabled =
        sources.filter(
            source => source.enabled !== false
        ).length;

    $("sourceEnabled").textContent =
        formatNumber(enabled);

    let online = 0;
    let offline = 0;

    sources.forEach(source => {

        const status =
            sourceStatus(source);

        if (status.className === "online") online++;
        if (status.className === "offline") offline++;

    });

    $("sourceOnline").textContent =
        formatNumber(online);

    $("sourceOffline").textContent =
        formatNumber(offline);

    $("sourceGrid").innerHTML =
        sources.map(source => {

            const status =
                sourceStatus(source);

            const latest =
                getSourceLatestSync(source);

            return `
                <article class="source-card">

                    <div class="source-card-top">

                        <div class="source-icon">
                            ${escapeHTML(
                                String(source.name || "S")
                                    .charAt(0)
                                    .toUpperCase()
                            )}
                        </div>

                        <div>

                            <h3>
                                ${escapeHTML(source.name)}
                            </h3>

                            <small>
                                ${escapeHTML(source.type)}
                            </small>

                        </div>

                        <span class="source-status ${status.className}">
                            ${status.label}
                        </span>

                    </div>

                    <div class="source-url">
                        ${escapeHTML(source.url)}
                    </div>

                    <div class="source-details">

                        <div>
                            <span>ENABLED</span>
                            <strong>
                                ${source.enabled === false
                                    ? "NO"
                                    : "YES"}
                            </strong>
                        </div>

                        <div>
                            <span>SCHEDULE</span>
                            <strong>
                                ${escapeHTML(
                                    source.schedule_minutes || "-"
                                )} MIN
                            </strong>
                        </div>

                        <div>
                            <span>LAST SYNC</span>
                            <strong>
                                ${latest
                                    ? escapeHTML(
                                        formatTime(
                                            latest.completed_at ||
                                            latest.started_at
                                        )
                                    )
                                    : "NEVER"}
                            </strong>
                        </div>

                        <div>
                            <span>RECORDS</span>
                            <strong>
                                ${latest
                                    ? formatNumber(
                                        latest.records_found
                                    )
                                    : "0"}
                            </strong>
                        </div>

                    </div>

                    <div class="source-actions">

                        <button
                            onclick="syncSource('${escapeHTML(source.id)}')">
                            SYNC NOW
                        </button>

                        <button
                            onclick="toggleSource('${escapeHTML(source.id)}')">
                            ${source.enabled === false
                                ? "ENABLE"
                                : "DISABLE"}
                        </button>

                        <button
                            class="danger-button"
                            onclick="deleteSource('${escapeHTML(source.id)}')">
                            DELETE
                        </button>

                    </div>

                </article>
            `;

        }).join("");

    if (!sources.length) {

        $("sourceGrid").innerHTML =
            `<div class="empty">
                No connected sources configured.
            </div>`;
    }
}

function renderSync() {

    const records =
        [...syncRecords]
            .sort(
                (a, b) =>
                    new Date(b.started_at || 0) -
                    new Date(a.started_at || 0)
            );

    $("syncTable").innerHTML =
        records.map(record => {

            const status =
                String(record.status || "")
                    .toLowerCase();

            return `
                <tr>

                    <td>
                        ${escapeHTML(
                            formatTime(record.started_at)
                        )}
                    </td>

                    <td>
                        ${escapeHTML(record.source_name)}
                    </td>

                    <td>
                        ${escapeHTML(record.source_type)}
                    </td>

                    <td>
                        <span class="status ${escapeHTML(status)}">
                            ${escapeHTML(
                                String(
                                    record.status || ""
                                ).toUpperCase()
                            )}
                        </span>
                    </td>

                    <td>
                        ${formatNumber(record.records_found)}
                    </td>

                    <td>
                        ${formatNumber(record.records_created)}
                    </td>

                    <td>
                        ${formatNumber(record.records_updated)}
                    </td>

                    <td>
                        ${formatNumber(record.records_failed)}
                    </td>

                    <td>
                        ${escapeHTML(record.message || "")}
                    </td>

                </tr>
            `;

        }).join("");

    if (!records.length) {

        $("syncTable").innerHTML =
            `<tr>
                <td colspan="9" class="empty">
                    No synchronization history.
                </td>
            </tr>`;
    }
}

function renderAudit() {

    const query =
        ($("auditSearch").value || "")
            .trim()
            .toLowerCase();

    const action =
        $("auditAction").value;

    const filtered =
        auditRecords.filter(record => {

            const actionMatch =
                !action ||
                String(record.action || "")
                    .toUpperCase() === action;

            const text = [
                record.action,
                record.entity_type,
                record.asset_code,
                record.source,
                record.description
            ]
            .join(" ")
            .toLowerCase();

            return actionMatch &&
                text.includes(query);
        });

    $("auditTable").innerHTML =
        filtered.map(record => {

            return `
                <tr>

                    <td>
                        ${escapeHTML(
                            formatTime(record.created_at)
                        )}
                    </td>

                    <td>
                        <span class="status">
                            ${escapeHTML(record.action)}
                        </span>
                    </td>

                    <td>
                        ${escapeHTML(record.entity_type)}
                    </td>

                    <td class="code">
                        ${escapeHTML(record.asset_code)}
                    </td>

                    <td>
                        ${escapeHTML(record.source)}
                    </td>

                    <td>
                        ${escapeHTML(record.description)}
                    </td>

                </tr>
            `;

        }).join("");

    if (!filtered.length) {

        $("auditTable").innerHTML =
            `<tr>
                <td colspan="6" class="empty">
                    No audit events found.
                </td>
            </tr>`;
    }
}

async function syncSource(id) {

    notify(
        "Starting synchronization...",
        "normal"
    );

    try {

        const result =
            await getJSON(
                `${API}/automation/run/${encodeURIComponent(id)}`,
                {
                    method: "POST"
                }
            );

        notify(
            "Synchronization started.",
            "success"
        );

        await refreshEverything();

    } catch (error) {

        notify(
            "Synchronization failed: " +
            error.message,
            "error"
        );
    }
}

async function toggleSource(id) {

    const source =
        sources.find(
            x => String(x.id) === String(id)
        );

    if (!source) return;

    const enabled =
        source.enabled === false;

    try {

        await getJSON(
            `${API}/automation/sources/${encodeURIComponent(id)}`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    enabled
                })
            }
        );

        notify(
            enabled
                ? "Source enabled."
                : "Source disabled.",
            "success"
        );

        await loadSources();

    } catch (error) {

        notify(
            "Source update failed: " +
            error.message,
            "error"
        );
    }
}

async function deleteSource(id) {

    const confirmed =
        confirm(
            "Delete this source from the ATUL source registry?"
        );

    if (!confirmed) return;

    try {

        await getJSON(
            `${API}/automation/sources/${encodeURIComponent(id)}`,
            {
                method: "DELETE"
            }
        );

        notify(
            "Source deleted.",
            "success"
        );

        await loadSources();

    } catch (error) {

        notify(
            "Source deletion failed: " +
            error.message,
            "error"
        );
    }
}

async function syncAll() {

    if (!sources.length) {

        notify(
            "No sources configured.",
            "error"
        );

        return;
    }

    notify(
        "Starting synchronization for all sources...",
        "normal"
    );

    for (const source of sources) {

        if (source.enabled === false) continue;

        try {

            await fetch(
                `${API}/automation/run/${encodeURIComponent(source.id)}`,
                {
                    method: "POST"
                }
            );

        } catch (error) {

            console.error(error);
        }
    }

    notify(
        "Synchronization requests submitted.",
        "success"
    );

    setTimeout(
        refreshEverything,
        1500
    );
}

async function createSource(event) {

    event.preventDefault();

    const source = {

        id: $("sourceId").value.trim(),

        name: $("sourceName").value.trim(),

        type: $("sourceType").value,

        url: $("sourceUrl").value.trim(),

        method: "GET",

        headers: {},

        params: {},

        timeout: 30,

        enabled: true,

        schedule_minutes:
            Number(
                $("sourceSchedule").value
            ),

        asset_mapping: {

            asset_code:
                $("mapAssetCode").value.trim(),

            name:
                $("mapAssetName").value.trim(),

            description:
                $("mapDescription").value.trim()
        }
    };

    try {

        await getJSON(
            `${API}/automation/sources`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(source)
            }
        );

        notify(
            "Source created successfully.",
            "success"
        );

        closeSourceModal();

        await loadSources();

    } catch (error) {

        notify(
            "Source creation failed: " +
            error.message,
            "error"
        );
    }
}

function exportJSON(filename, data) {

    const blob =
        new Blob(
            [JSON.stringify(data, null, 2)],
            {
                type: "application/json"
            }
        );

    const url =
        URL.createObjectURL(blob);

    const a =
        document.createElement("a");

    a.href = url;
    a.download = filename;

    a.click();

    URL.revokeObjectURL(url);
}

function exportCSV(filename, rows) {

    if (!rows.length) {

        notify(
            "Nothing to export.",
            "error"
        );

        return;
    }

    const keys =
        Object.keys(rows[0]);

    const csv = [
        keys.join(","),
        ...rows.map(row =>
            keys.map(key => {

                const value =
                    row[key] ?? "";

                return '"' +
                    String(value)
                        .replaceAll('"', '""') +
                    '"';

            }).join(",")
        )
    ].join("\n");

    const blob =
        new Blob(
            [csv],
            {
                type: "text/csv"
            }
        );

    const url =
        URL.createObjectURL(blob);

    const a =
        document.createElement("a");

    a.href = url;

    a.download =
        filename;

    a.click();

    URL.revokeObjectURL(url);
}

function openSourceModal() {

    $("sourceModal")
        .classList.add("open");
}

function closeSourceModal() {

    $("sourceModal")
        .classList.remove("open");

    $("sourceForm").reset();
}

async function refreshEverything() {

    await Promise.all([
        loadDashboard(),
        loadAssets(),
        loadSources(),
        loadSync(),
        loadAudit(),
        loadHealth()
    ]);

    $("systemStatus").textContent =
        "SYSTEM ONLINE";

    $("systemStatus")
        .previousElementSibling
        .classList.remove("offline");
}

function setupNavigation() {

    document
        .querySelectorAll(".nav-button")
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    document
                        .querySelectorAll(".nav-button")
                        .forEach(x =>
                            x.classList.remove("active")
                        );

                    button.classList.add("active");

                    document
                        .querySelectorAll(".dashboard-section")
                        .forEach(section =>
                            section.classList.remove("active")
                        );

                    const target =
                        $(button.dataset.section);

                    if (target) {
                        target.classList.add("active");
                    }

                }
            );
        });
}

function updateClock() {

    $("liveClock").textContent =
        new Date().toLocaleTimeString();
}

function setupEvents() {

    $("refreshButton")
        .addEventListener(
            "click",
            refreshEverything
        );

    $("healthRefresh")
        .addEventListener(
            "click",
            loadHealth
        );

    $("syncAllButton")
        .addEventListener(
            "click",
            syncAll
        );

    $("addSourceButton")
        .addEventListener(
            "click",
            openSourceModal
        );

    $("closeSourceModal")
        .addEventListener(
            "click",
            closeSourceModal
        );

    $("cancelSource")
        .addEventListener(
            "click",
            closeSourceModal
        );

    $("sourceForm")
        .addEventListener(
            "submit",
            createSource
        );

    $("assetSearch")
        .addEventListener(
            "input",
            renderAssets
        );

    $("auditSearch")
        .addEventListener(
            "input",
            renderAudit
        );

    $("auditAction")
        .addEventListener(
            "change",
            renderAudit
        );

    $("fullscreenButton")
        .addEventListener(
            "click",
            async () => {

                if (!document.fullscreenElement) {

                    await document.documentElement
                        .requestFullscreen();

                } else {

                    await document.exitFullscreen();
                }
            }
        );

    $("themeButton")
        .addEventListener(
            "click",
            () => {

                document.body.classList.toggle(
                    "alternate-theme"
                );

            }
        );

    $("exportActivity")
        .addEventListener(
            "click",
            () =>
                exportJSON(
                    "atul-recent-activity.json",
                    dashboardData.recent_audit || []
                )
        );

    $("exportAudit")
        .addEventListener(
            "click",
            () =>
                exportCSV(
                    "atul-audit.csv",
                    auditRecords
                )
        );

    $("sourceModal")
        .addEventListener(
            "click",
            event => {

                if (
                    event.target ===
                    $("sourceModal")
                ) {
                    closeSourceModal();
                }
            }
        );

    document.addEventListener(
        "keydown",
        event => {

            if (event.key === "Escape") {
                closeSourceModal();
            }

            if (
                event.key.toLowerCase() === "r" &&
                !event.ctrlKey &&
                !event.metaKey
            ) {
                refreshEverything();
            }

        }
    );
}

window.syncSource = syncSource;
window.toggleSource = toggleSource;
window.deleteSource = deleteSource;

setupNavigation();
setupEvents();
updateClock();

setInterval(
    updateClock,
    1000
);

setInterval(
    refreshEverything,
    30000
);

refreshEverything();
