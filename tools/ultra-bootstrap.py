#!/usr/bin/env python3
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path.cwd()
SOURCE = Path(sys.argv[1]).resolve()
PLUS_SHA = "356ba98a7ab479caf1b64526133f05944ce17efc"
ULTRA_BASE = "cc350568cc3d4a900896a75a6d843f01189b5b87"
BRANCH = "codex/insfav-ultra-bootstrap"

def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)

assert subprocess.check_output(["git", "branch", "--show-current"], text=True).strip() == BRANCH
assert subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip().removesuffix(".git").endswith("/INSFAV-Ultra")
run(["git", "merge-base", "--is-ancestor", ULTRA_BASE, "HEAD"])
assert subprocess.check_output(["git", "status", "--porcelain"], text=True).strip() == "", "Refusing to overwrite a dirty Ultra worktree"
assert subprocess.check_output(["git", "-C", str(SOURCE), "rev-parse", "HEAD"], text=True).strip() == PLUS_SHA, "Pinned Plus source SHA mismatch"

license_text = subprocess.check_output(["git", "show", ULTRA_BASE + ":LICENSE"], text=True)
workflow_backup = Path(os.environ["RUNNER_TEMP"]) / "ultra-bootstrap.yml"
shutil.copy2(ROOT / ".github/workflows/ultra-bootstrap.yml", workflow_backup)

run(["rsync", "-a", "--delete", "--exclude=.git", str(SOURCE) + "/", str(ROOT) + "/"])
(ROOT / "LICENSE").write_text(
    license_text.replace("Copyright (c) 2026 BlackWare", "Copyright (c) 2026 BlackWare\nCopyright (c) 2026 BlackWare-AI", 1),
    encoding="utf-8"
)
(ROOT / ".github/workflows/ultra-bootstrap.yml").parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(workflow_backup, ROOT / ".github/workflows/ultra-bootstrap.yml")

# Rewrite the source repository identity without changing the Java namespace or source packages.
extensions = {".gradle", ".properties", ".xml", ".java", ".kt", ".js", ".css", ".html",
              ".json", ".yml", ".yaml", ".md", ".tsv", ".txt", ".py", ".cjs", ".sh", ".toml", ".rs"}
replacements = [
    ("com.instagram.insfav.plus.test", "com.instagram.insfav.ultra.test"),
    ("com.instagram.insfav.plus", "com.instagram.insfav.ultra"),
    ("BlackWare-AI/INSFAV-Plus", "BlackWare-AI/INSFAV-Ultra"),
    ("INSFAV-Plus", "INSFAV-Ultra"),
    ("INSFAV Plus", "INSFAV Ultra"),
    ("const plus=require('../package.json').name.includes('plus')", "const plus=true"),
    ("insfav-plus", "insfav-ultra"),
    ("insfav_plus", "insfav_ultra"),
    ("plus-release", "ultra-release"),
    ("INSFAV_KEYSTORE", "ULTRA_RELEASE_KEYSTORE"),
    ("INSFAV_STORE_PASSWORD", "ULTRA_RELEASE_STORE_PASSWORD"),
    ("INSFAV_KEY_PASSWORD", "ULTRA_RELEASE_KEY_PASSWORD"),
    ("INSFAV_KEY_ALIAS", "ULTRA_RELEASE_KEY_ALIAS"),
    ("PLUS_KEYSTORE_BASE64", "ULTRA_RELEASE_KEYSTORE_BASE64"),
    ("PLUS_STORE_PASSWORD", "ULTRA_RELEASE_STORE_PASSWORD"),
    ("PLUS_KEY_PASSWORD", "ULTRA_RELEASE_KEY_PASSWORD"),
    ("PLUS_KEY_ALIAS", "ULTRA_RELEASE_KEY_ALIAS"),
    ("secrets.KEYSTORE_BASE64", "secrets.ULTRA_RELEASE_KEYSTORE_BASE64"),
    ("secrets.KEYSTORE_PASSWORD", "secrets.ULTRA_RELEASE_STORE_PASSWORD"),
    ("secrets.KEY_PASSWORD", "secrets.ULTRA_RELEASE_KEY_PASSWORD"),
    ("secrets.KEY_ALIAS", "secrets.ULTRA_RELEASE_KEY_ALIAS"),
    ("plus-v", "ultra-v"),
    ("INSFAV-Plus-", "INSFAV-Ultra-"),
    ("cffc756bf3d517b02780093e7d0d80ae737ce9e3b035a86a094f5698ffab35c8", "41603cb287ae84753f5c203ed9871a4780672f51643cd7c7df386c5b94bed664"),
    ("fetcher-queue.db", "ultra-fetcher-queue.db"),
    ("fetcher-cookies.enc", "ultra-fetcher-cookies.enc"),
    ("instagram-webview-cookies.enc", "ultra-instagram-webview-cookies.enc"),
    ("instagram-netscape-cookies.enc", "ultra-instagram-netscape-cookies.enc"),
    ("thumbnail-fetcher", "ultra-thumbnail-fetcher"),
    ("insfav.cookie.aes.v1", "insfav.ultra.cookie.aes.v1"),
    ("insfav-next-profile", "insfav-ultra-next-profile"),
    ("insfav-queue-recovery", "insfav-ultra-queue-recovery"),
]
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in extensions:
        continue
    try:
        value = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    original = value
    for old, new in replacements:
        value = value.replace(old, new)
    if path.name in {"package.json", "package-lock.json"}:
        value = value.replace("insfav-plus-build-tools", "insfav-ultra-build-tools")
    if value != original:
        path.write_text(value, encoding="utf-8")

updates_test = ROOT / "app/src/test/java/com/instagram/insfav/updates/AppUpdatesTest.java"
if updates_test.exists():
    value = updates_test.read_text(encoding="utf-8")
    value = value.replace(
        'app.endsWith("plus")?"BlackWare-AI/INSFAV":"BlackWare-AI/INSFAV-Ultra"',
        'app.endsWith(".ultra")?"BlackWare-AI/INSFAV-Plus":"BlackWare-AI/INSFAV-Ultra"'
    )
    value = value.replace(
        'c.getPackageName().endsWith(".plus")?"com.instagram.insfav":"com.instagram.insfav.ultra"',
        'c.getPackageName().endsWith(".ultra")?"com.instagram.insfav":"com.instagram.insfav.ultra"'
    )
    updates_test.write_text(value, encoding="utf-8")

(ROOT / "version.properties").write_text("VERSION_NAME=1.0.0\nVERSION_CODE=1\n", encoding="utf-8")
settings = ROOT / "settings.gradle"
settings.write_text(settings.read_text().replace("rootProject.name = 'INSFAV'", "rootProject.name = 'INSFAV Ultra'"), encoding="utf-8")

readme = ROOT / "README.md"
value = readme.read_text(encoding="utf-8")
value = re.sub(r"\[[^\]]*(?:yayımlanan|latest|signed)[^\]]*\]\(https://github\.com/BlackWare-AI/INSFAV-Ultra/releases/latest\)",
               "İlk Ultra sürümü henüz yayımlanmadı.", value, count=1, flags=re.I)
readme.write_text(value, encoding="utf-8")

agents = """# INSFAV Ultra development

- Work only in BlackWare-AI/INSFAV-Ultra; never modify INSFAV-Plus.
- web/ is the authoritative UI source. Rebuild packaged assets with npm run web.
- Keep the Android namespace com.instagram.insfav; the installable application ID is com.instagram.insfav.ultra.
- Keep Ultra private storage, preferences, databases, WebView data, notification channels, WorkManager names and Keystore aliases isolated.
- Preserve original JSON data and unknown fields, SQLite/queue schemas, cookie AES-GCM format, thumbnail naming and 128/256px compatibility.
- Do not add network endpoints, scraping/login behavior, or launch-time background work.
- Release signing reads only ULTRA_RELEASE_* environment variables / GitHub Actions secrets. Never commit keys or print credentials.
"""
(ROOT / "AGENTS.md").write_text(agents, encoding="utf-8")

# Private-state identifiers are UID isolated by Android; additionally scope stable identifiers explicitly.
scoped = {
    "thumbnail-fetcher": "ultra-thumbnail-fetcher",
    "fetcher-queue.db": "ultra-fetcher-queue.db",
    "insfav.cookie.aes.v1": "insfav.ultra.cookie.aes.v1",
    "fetcher-cookies.enc": "ultra-fetcher-cookies.enc",
    "instagram-webview-cookies.enc": "ultra-instagram-webview-cookies.enc",
    "instagram-netscape-cookies.enc": "ultra-instagram-netscape-cookies.enc",
    '"downloads"': '"ultra-downloads"',
    '"downloads", "Thumbnail downloads"': '"ultra-downloads", "INSFAV Ultra · Thumbnail downloads"',
    '"insfav-next-profile"': '"insfav-ultra-next-profile"',
    '"insfav-queue-recovery"': '"insfav-ultra-queue-recovery"',
}
for rel in [
    "app/src/main/java/com/instagram/insfav/fetcher/SessionState.java",
    "app/src/main/java/com/instagram/insfav/fetcher/QueueStore.java",
    "app/src/main/java/com/instagram/insfav/fetcher/CookieVault.java",
    "app/src/main/java/com/instagram/insfav/fetcher/NetscapeBrowserCookies.java",
    "app/src/main/java/com/instagram/insfav/fetcher/DownloadNotification.java",
    "app/src/main/java/com/instagram/insfav/fetcher/WorkScheduler.java",
]:
    p = ROOT / rel
    text = p.read_text(encoding="utf-8")
    for old, new in scoped.items():
        text = text.replace(old, new)
    p.write_text(text, encoding="utf-8")

# Robolectric and instrumentation fixtures must address Ultra's isolated storage names.
# The source rename is intentionally mirrored only in test fixtures; persisted JSON,
# SQLite table layouts, cookie payloads, and migration schemas remain unchanged.
for test_root in [ROOT / "app/src/test/java", ROOT / "app/src/androidTest/java"]:
    if not test_root.exists():
        continue
    for p in test_root.rglob("*.java"):
        value = p.read_text(encoding="utf-8")
        original = value
        for legacy, ultra in scoped.items():
            value = value.replace(legacy, ultra)
        if value != original:
            p.write_text(value, encoding="utf-8")

# Tests that exercise foreign-app rejection must keep the other app as the negative fixture.
updates_test = ROOT / "app/src/test/java/com/instagram/insfav/updates/AppUpdatesTest.java"
if updates_test.exists():
    value = updates_test.read_text(encoding="utf-8")
    value = value.replace('app.endsWith("plus")?"BlackWare-AI/INSFAV":"BlackWare-AI/INSFAV-Ultra"',
                          'app.endsWith("ultra")?"BlackWare-AI/INSFAV":"BlackWare-AI/INSFAV-Ultra"')
    value = value.replace('c.getPackageName().endsWith(".plus")?"com.instagram.insfav":"com.instagram.insfav.ultra"',
                          'c.getPackageName().endsWith(".ultra")?"com.instagram.insfav":"com.instagram.insfav.ultra"')
    updates_test.write_text(value, encoding="utf-8")

# Rename Plus-only publisher helper scripts to Ultra names.
for old, new in [
    ("tools/publish-plus.py", "tools/publish-ultra.py"),
    ("tools/test-publish-plus.py", "tools/test-publish-ultra.py"),
]:
    src, dst = ROOT / old, ROOT / new
    if src.exists():
        src.rename(dst)
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix.lower() in extensions:
            try: s = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError): continue
            ns = s.replace(old, new)
            if ns != s: p.write_text(ns, encoding="utf-8")

# Reproducible optional Rust/JNI build. The production native path stays disabled until
# same-runner results show a repeatable >=15% win without regressions.
gradle = ROOT / "app/build.gradle"
g = gradle.read_text(encoding="utf-8")
g = g.replace("rootProject.file('version.properties').withInputStream { appVersion.load(it) }",
              "rootProject.file('version.properties').withInputStream { appVersion.load(it) }\ndef ultraNativeCore = project.findProperty('ultraNativeCore')?.toString() == 'true'")
g = g.replace("testApplicationId 'com.instagram.insfav.ultra.test';",
              "testApplicationId 'com.instagram.insfav.ultra.test'; buildConfigField 'boolean', 'ULTRA_NATIVE_CORE', ultraNativeCore.toString();")
if "jniLibs.srcDir" not in g:
    g = g.replace("buildFeatures { buildConfig true }",
                  "buildFeatures { buildConfig true }\n    sourceSets { main { jniLibs.srcDir(layout.buildDirectory.dir('generated/ultraJniLibs')) } }")
if "buildRustCore" not in g:
    insertion = """
if (ultraNativeCore) {
    tasks.register('buildRustCore', Exec) {
        workingDir rootProject.file('rust/insfav-core')
        commandLine 'cargo', 'ndk', '-t', 'arm64-v8a', '-t', 'armeabi-v7a', '-t', 'x86_64',
                '-o', layout.buildDirectory.dir('generated/ultraJniLibs').get().asFile.absolutePath,
                'build', '--release'
    }
    tasks.named('preBuild').configure { dependsOn('buildRustCore') }
}
"""
    g = g.replace("\ndependencies {", "\n" + insertion + "\ndependencies {")
gradle.write_text(g, encoding="utf-8")

rust = ROOT / "rust/insfav-core"
(rust / "src").mkdir(parents=True, exist_ok=True)
(rust / "Cargo.toml").write_text("""[package]
name = "insfav-core"
version = "0.1.0"
edition = "2021"
publish = false

[lib]
name = "insfav_core"
crate-type = ["cdylib", "rlib"]

[dependencies]
jni = "=0.21.1"
serde = { version = "=1.0.219", features = ["derive"] }
serde_json = { version = "=1.0.140" }
""", encoding="utf-8")
(ROOT / "rust/rust-toolchain.toml").write_text("""[toolchain]
channel = "1.88.0"
profile = "minimal"
targets = ["aarch64-linux-android", "armv7-linux-androideabi", "x86_64-linux-android"]
""", encoding="utf-8")

(rust / "src/lib.rs").write_text(r'''use jni::objects::{JByteArray, JClass};
use jni::sys::jbyteArray;
use jni::JNIEnv;
use serde::Serialize;
use serde_json::Value;
use std::collections::HashSet;
use std::panic::{catch_unwind, AssertUnwindSafe};

#[derive(Debug, Serialize, PartialEq, Eq)]
pub struct ParsedUsers { users: Vec<String>, total: usize }

fn collections(root: Value) -> Result<Vec<Value>, String> {
    match root {
        Value::Array(items) => Ok(items),
        Value::Object(mut object) => match object.remove("favorite_page_pref") {
            Some(Value::Array(items)) => Ok(items),
            Some(Value::String(nested)) => match serde_json::from_str::<Value>(&nested).map_err(|e| e.to_string())? {
                Value::Array(items) => Ok(items),
                _ => Err("Invalid collection array".into()),
            },
            _ => Err("Missing collection array".into()),
        },
        _ => Err("Invalid collection document".into()),
    }
}

pub fn parse_users(input: &[u8]) -> Result<ParsedUsers, String> {
    let root = serde_json::from_slice::<Value>(input).map_err(|e| e.to_string())?;
    let groups = collections(root)?;
    let mut users = Vec::new();
    let mut seen = HashSet::new();
    let mut total = 0usize;
    for group in groups {
        let object = group.as_object().ok_or("Invalid collection")?;
        if object.get("name").and_then(Value::as_str).is_none() {
            return Err("Invalid collection name".into());
        }
        let items = object.get("items").and_then(Value::as_array).ok_or("Invalid collection items")?;
        total = total.saturating_add(items.len());
        for item in items {
            let page_id = item.as_object()
                .and_then(|v| v.get("pageId"))
                .and_then(Value::as_str)
                .ok_or("Invalid account fields")?;
            let trimmed = page_id.trim();
            let without_at = trimmed.strip_prefix('@').unwrap_or(trimmed);
            let normalized = without_at.to_lowercase();
            if !normalized.is_empty() && seen.insert(normalized.clone()) {
                users.push(normalized);
            }
        }
    }
    Ok(ParsedUsers { users, total })
}

fn empty_result(env: &mut JNIEnv) -> jbyteArray {
    env.byte_array_from_slice(&[])
        .map(|array| array.into_raw())
        .unwrap_or(std::ptr::null_mut())
}

#[no_mangle]
pub extern "system" fn Java_com_instagram_insfav_NativeCore_nativeUniqueUsers(
    mut env: JNIEnv, _class: JClass, input: JByteArray,
) -> jbyteArray {
    let result = catch_unwind(AssertUnwindSafe(|| {
        let bytes = env.convert_byte_array(input).map_err(|e| e.to_string())?;
        let parsed = parse_users(&bytes)?;
        serde_json::to_vec(&parsed).map_err(|e| e.to_string())
    }));
    match result {
        Ok(Ok(bytes)) => env.byte_array_from_slice(&bytes)
            .map(|array| array.into_raw())
            .unwrap_or(std::ptr::null_mut()),
        _ => empty_result(&mut env),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn array_and_duplicate_order() {
        let raw = br#"[{"name":"A","items":[{"pageId":" @Alice "},{"pageId":"bob"},{"pageId":"ALICE"}]}]"#;
        let parsed = parse_users(raw).unwrap();
        assert_eq!(parsed.users, vec!["alice", "bob"]);
        assert_eq!(parsed.total, 3);
    }

    #[test]
    fn nested_favorite_page_pref_string() {
        let nested = r#"[{"name":"Saved","items":[{"pageId":"USER"}]}]"#;
        let raw = serde_json::to_vec(&serde_json::json!({"favorite_page_pref": nested})).unwrap();
        assert_eq!(parse_users(&raw).unwrap().users, vec!["user"]);
    }

    #[test]
    fn empty_and_malformed_boundaries() {
        assert_eq!(parse_users(br#"[]"#).unwrap(), ParsedUsers { users: vec![], total: 0 });
        assert!(parse_users(b"{").is_err());
        assert!(parse_users(br#"{"favorite_page_pref":"{}"}"#).is_err());
        assert!(parse_users(br#"[{"name":"x","items":[{}]}]"#).is_err());
    }

    #[test]
    fn fifteen_thousand_records() {
        let mut items = Vec::new();
        for i in 0..15_000 { items.push(serde_json::json!({"pageId": format!("User{}", i % 10_000)})); }
        let raw = serde_json::to_vec(&serde_json::json!([{"name":"large","items":items}])).unwrap();
        let parsed = parse_users(&raw).unwrap();
        assert_eq!(parsed.total, 15_000);
        assert_eq!(parsed.users.len(), 10_000);
        assert_eq!(parsed.users[0], "user0");
        assert_eq!(parsed.users[9_999], "user9999");
    }

    #[test]
    fn repeated_memberships_keep_total() {
        let raw = br#"[{"name":"one","items":[{"pageId":"same"}]},{"name":"two","items":[{"pageId":"same"}]}]"#;
        let parsed = parse_users(raw).unwrap();
        assert_eq!(parsed.users, vec!["same"]);
        assert_eq!(parsed.total, 2);
    }
}
''', encoding="utf-8")

java = ROOT / "app/src/main/java/com/instagram/insfav/NativeCore.java"
java.write_text(r'''package com.instagram.insfav;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashSet;

/** Optional batch JNI facade. Java remains authoritative until a measured Rust win is accepted. */
public final class NativeCore {
    public static final class Result {
        public final LinkedHashSet<String> users;
        public final int total;
        Result(LinkedHashSet<String> users, int total) { this.users = users; this.total = total; }
    }
    private static final boolean LIBRARY_AVAILABLE;
    static {
        boolean loaded = false;
        if (BuildConfig.ULTRA_NATIVE_CORE) {
            try { System.loadLibrary("insfav_core"); loaded = true; }
            catch (LinkageError | SecurityException unavailable) { loaded = false; }
        }
        LIBRARY_AVAILABLE = loaded;
    }
    private NativeCore() {}
    public static boolean libraryAvailable() { return LIBRARY_AVAILABLE; }
    public static boolean enabled() { return BuildConfig.ULTRA_NATIVE_CORE && LIBRARY_AVAILABLE; }

    public static Result parse(String raw) throws JSONException {
        if (enabled()) {
            try {
                byte[] encoded = nativeUniqueUsers(raw.getBytes(StandardCharsets.UTF_8));
                if (encoded != null && encoded.length > 0) return decode(encoded);
            } catch (JSONException | LinkageError | RuntimeException ignored) {
                // Native failure falls back to the complete Java implementation.
            }
        }
        return parseJava(raw);
    }
    static Result parseJava(String raw) throws JSONException {
        LinkedHashSet<String> users = new LinkedHashSet<>();
        int count = 0;
        if (raw != null && !raw.isEmpty()) {
            JSONArray collections = Store.collections(raw);
            for (int i = 0; i < collections.length(); i++) {
                JSONArray items = collections.getJSONObject(i).getJSONArray("items");
                count += items.length();
                for (int j = 0; j < items.length(); j++) {
                    String user = ThumbnailPolicy.normalize(items.getJSONObject(j).getString("pageId"));
                    if (!user.isEmpty()) users.add(user);
                }
            }
        }
        return new Result(users, count);
    }
    static Result parseNativeForTest(String raw) throws JSONException {
        if (!LIBRARY_AVAILABLE) throw new IllegalStateException("Rust JNI library is not packaged");
        byte[] result = nativeUniqueUsers(raw.getBytes(StandardCharsets.UTF_8));
        if (result == null || result.length == 0) throw new JSONException("Native parser rejected input");
        return decode(result);
    }
    private static Result decode(byte[] encoded) throws JSONException {
        JSONObject parsed = new JSONObject(new String(encoded, StandardCharsets.UTF_8));
        JSONArray array = parsed.getJSONArray("users");
        LinkedHashSet<String> users = new LinkedHashSet<>();
        for (int i = 0; i < array.length(); i++) users.add(array.getString(i));
        return new Result(users, parsed.getInt("total"));
    }
    private static native byte[] nativeUniqueUsers(byte[] input);
}
''', encoding="utf-8")

store = ROOT / "app/src/main/java/com/instagram/insfav/Store.java"
s = store.read_text(encoding="utf-8")
pattern = re.compile(r"  synchronized Set<String> users\(\) throws JSONException \{.*?\n  \}\n\n  /\*\* Fresh validation only:", re.S)
replacement = """  synchronized Set<String> users() throws JSONException {
    if (cachedUsers == null) {
      NativeCore.Result parsed = NativeCore.parse(original());
      cachedUsers = parsed.users;
      total = parsed.total;
    }
    return Collections.unmodifiableSet(cachedUsers);
  }

  /** Fresh validation only:"""
s2, n = pattern.subn(replacement, s, count=1)
assert n == 1, "Could not safely replace Store.users()"
store.write_text(s2, encoding="utf-8")

unit_test = ROOT / "app/src/test/java/com/instagram/insfav/NativeCoreTest.java"
unit_test.parent.mkdir(parents=True, exist_ok=True)
unit_test.write_text(r'''package com.instagram.insfav;

import static org.junit.Assert.*;
import org.junit.Test;
import org.json.JSONException;

public class NativeCoreTest {
    @Test public void javaFallbackMatchesArrayAndWrapperFixtures() throws Exception {
        String array = "[{\"name\":\"A\",\"items\":[{\"pageId\":\" @Alice \"},{\"pageId\":\"bob\"},{\"pageId\":\"ALICE\"}]}]";
        NativeCore.Result result = NativeCore.parseJava(array);
        assertEquals(2, result.users.size());
        assertTrue(result.users.contains("alice"));
        assertEquals(3, result.total);
        String nested = "{\"favorite_page_pref\":\"[{\\\"name\\\":\\\"Saved\\\",\\\"items\\\":[{\\\"pageId\\\":\\\"USER\\\"}]}]\"}";
        assertEquals("user", NativeCore.parseJava(nested).users.iterator().next());
    }
    @Test public void javaFallbackHandlesEmptyDuplicateAndLargeInputs() throws Exception {
        assertEquals(0, NativeCore.parseJava("[]").total);
        String raw = "[{\"name\":\"a\",\"items\":[{\"pageId\":\"x\"},{\"pageId\":\"x\"}]}]";
        NativeCore.Result duplicate = NativeCore.parseJava(raw);
        assertEquals(1, duplicate.users.size());
        assertEquals(2, duplicate.total);
        StringBuilder large = new StringBuilder("[{\"name\":\"large\",\"items\":[");
        for (int i = 0; i < 15_000; i++) {
            if (i > 0) large.append(',');
            large.append("{\"pageId\":\"user").append(i % 10_000).append("\"}");
        }
        large.append("]}]");
        NativeCore.Result result = NativeCore.parseJava(large.toString());
        assertEquals(15_000, result.total);
        assertEquals(10_000, result.users.size());
    }
    @Test public void malformedDocumentsRemainErrors() {
        try { NativeCore.parseJava("{"); fail("malformed JSON must fail"); }
        catch (JSONException expected) { }
        try { NativeCore.parseJava("[{\"name\":\"x\",\"items\":[{}]}]"); fail("missing pageId must fail"); }
        catch (JSONException expected) { }
    }
}
''', encoding="utf-8")
native_test_value = unit_test.read_text(encoding="utf-8")
native_test_value = native_test_value.replace(
    "import org.junit.Test;",
    "import org.junit.Test;\nimport org.junit.runner.RunWith;\nimport org.robolectric.RobolectricTestRunner;"
)
native_test_value = native_test_value.replace(
    "import org.robolectric.RobolectricTestRunner;",
    "import org.robolectric.RobolectricTestRunner;\nimport org.robolectric.annotation.Config;"
)
native_test_value = native_test_value.replace(
    "public class NativeCoreTest {",
    "@RunWith(RobolectricTestRunner.class)\n@Config(sdk = 28, manifest = Config.NONE)\npublic class NativeCoreTest {"
)
unit_test.write_text(native_test_value, encoding="utf-8")

# Android 8+ rejects foreground notifications whose builder channel ID has no created channel.
notification_test = ROOT / "app/src/test/java/com/instagram/insfav/fetcher/DownloadNotificationTest.java"
notification_test.write_text(r'''package com.instagram.insfav.fetcher;

import static org.junit.Assert.*;
import android.app.Notification;
import android.app.NotificationManager;
import android.content.Context;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.annotation.Config;

@RunWith(RobolectricTestRunner.class)
@Config(sdk = 28, manifest = Config.NONE)
public class DownloadNotificationTest {
    @Test public void foregroundNotificationUsesAnExistingUltraChannelAndSmallIcon() {
        Context context = RuntimeEnvironment.getApplication();
        NotificationManager manager = context.getSystemService(NotificationManager.class);
        Notification notification = DownloadNotification.preparing(context);
        assertEquals("ultra-downloads", notification.getChannelId());
        assertNotNull(manager.getNotificationChannel(notification.getChannelId()));
        assertNotNull(notification.getSmallIcon());
    }
}
''', encoding="utf-8")

android_test = ROOT / "app/src/androidTest/java/com/instagram/insfav/NativeCoreInstrumentationTest.java"
android_test.parent.mkdir(parents=True, exist_ok=True)
android_test.write_text(r'''package com.instagram.insfav;

import static org.junit.Assert.*;
import org.junit.Test;

public class NativeCoreInstrumentationTest {
    private static String fixture(int count) {
        StringBuilder raw = new StringBuilder("[{\"name\":\"benchmark\",\"items\":[");
        for (int i = 0; i < count; i++) {
            if (i > 0) raw.append(',');
            raw.append("{\"pageId\":\"User").append(i % Math.max(1, count * 2 / 3)).append("\"}");
        }
        return raw.append("]}]").toString();
    }
    @Test public void nativeAndJavaAreEquivalentAcrossRequiredCases() throws Exception {
        assertTrue("Rust JNI library must be packaged for this instrumentation variant", NativeCore.libraryAvailable());
        String[] fixtures = {
            "[]",
            "[{\"name\":\"A\",\"items\":[{\"pageId\":\" @Alice \"},{\"pageId\":\"bob\"},{\"pageId\":\"ALICE\"}]}]",
            "{\"favorite_page_pref\":\"[{\\\"name\\\":\\\"Saved\\\",\\\"items\\\":[{\\\"pageId\\\":\\\"USER\\\"}]}]\"}",
            fixture(15_000)
        };
        for (String raw : fixtures) {
            NativeCore.Result java = NativeCore.parseJava(raw);
            NativeCore.Result rust = NativeCore.parseNativeForTest(raw);
            assertEquals(java.total, rust.total);
            assertEquals(java.users, rust.users);
        }
    }
    @Test public void benchmarkJavaAgainstRustAndEmitRawResults() throws Exception {
        assertTrue(NativeCore.libraryAvailable());
        StringBuilder report = new StringBuilder("{\"runner\":\"Android emulator x86_64\",\"rounds\":9,\"cases\":[");
        int[] sizes = {1_000, 10_000, 15_000};
        for (int c = 0; c < sizes.length; c++) {
            String raw = fixture(sizes[c]);
            long[] javaTimes = new long[9], rustTimes = new long[9];
            Runtime runtime = Runtime.getRuntime();
            long beforeUsed = runtime.totalMemory() - runtime.freeMemory();
            for (int i = 0; i < 9; i++) {
                long start = System.nanoTime(); NativeCore.parseJava(raw); javaTimes[i] = System.nanoTime() - start;
                start = System.nanoTime(); NativeCore.parseNativeForTest(raw); rustTimes[i] = System.nanoTime() - start;
            }
            long afterUsed = runtime.totalMemory() - runtime.freeMemory();
            java.util.Arrays.sort(javaTimes); java.util.Arrays.sort(rustTimes);
            if (c > 0) report.append(',');
            report.append("{\"records\":").append(sizes[c])
                .append(",\"javaMedianNs\":").append(javaTimes[4])
                .append(",\"rustJniMedianNs\":").append(rustTimes[4])
                .append(",\"javaNs\":").append(java.util.Arrays.toString(javaTimes))
                .append(",\"rustJniNs\":").append(java.util.Arrays.toString(rustTimes))
                .append(",\"heapDeltaBytes\":").append(afterUsed-beforeUsed).append('}');
        }
        report.append("]}");
        android.util.Log.i("INSFAV_ULTRA_NATIVE", "ULTRA_NATIVE_BENCHMARK_RAW=" + report);
    }
}
''', encoding="utf-8")

app_build = ROOT / "app/build.gradle"
g = app_build.read_text(encoding="utf-8")
if "androidTestImplementation" not in g:
    g = g.replace('testImplementation "org.robolectric:robolectric:4.14.1"',
                  'testImplementation "org.robolectric:robolectric:4.14.1"\n    androidTestImplementation "junit:junit:4.13.2"\n    androidTestImplementation "androidx.test:runner:1.6.2"\n    androidTestImplementation "androidx.test:core:1.6.1"')
app_build.write_text(g, encoding="utf-8")

# Single contextual quick-jump and immediate thumb drag.
html = ROOT / "web/index.html"
h = html.read_text(encoding="utf-8")
old_controls = re.compile(r'<button id="scroll-start".*?</button>\s*<button id="scroll-end".*?</button>', re.S)
new_controls = """<button id="scroll-jump" type="button" aria-label="Go to end of list" data-i18n-aria-label="Go to end of list"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 10 6 6 6-6"/></svg></button>"""
h, count = old_controls.subn(new_controls, h, count=1)
assert count == 1, "Main scrollbar buttons were not found in expected markup"
h = h.replace('</div></div>\n<p id="scroll-help"', '</div></div>\n<span id="scroll-position" role="status" aria-live="off" hidden>0%</span>\n<p id="scroll-help"', 1)
h = h.replace("Hold for 0.25 seconds to drag. Use arrow keys, Page Up, Page Down, Home or End to scroll.",
              "Drag the handle to scroll. Use arrow keys, Page Up, Page Down, Home or End to scroll.")
html.write_text(h, encoding="utf-8")

scroll = ROOT / "web/list-scroll.js"
scroll.write_text(r'''(function(root){
'use strict';
root.createListScroll=function(){
 const rail=document.getElementById('main-scroll');
 const track=document.getElementById('scroll-track');
 const thumb=document.getElementById('scroll-thumb');
 const mark=thumb.firstElementChild;
 const jump=document.getElementById('scroll-jump');
 const position=document.getElementById('scroll-position');
 const nav=document.querySelector('.bottom-nav');
 const app=document.getElementById('app');
 const pointers=new Set();
 let accounts=false,frame=0,hold=null,maximum=0,travel=0,viewport=0,viewportWidth=0,trackHeight=0,hideTimer=0,keyboard=false;
 const page=()=>document.scrollingElement;
 const locked=()=>document.body.classList.contains('overlay-open');
 const clamp=value=>Math.max(0,Math.min(maximum,value));
 const text=(key,values)=>root.InsfavI18n&&root.InsfavI18n.text?root.InsfavI18n.text(key,values):key;
 const reduced=()=>root.matchMedia&&root.matchMedia('(prefers-reduced-motion: reduce)').matches;
 function hideLater(){
  clearTimeout(hideTimer);
  if(!rail.hidden&&!hold&&!(keyboard&&rail.contains(document.activeElement)))
   hideTimer=setTimeout(()=>rail.classList.add('idle'),1800);
 }
 function wake(){rail.classList.remove('idle');hideLater();}
 function updateJump(top){
  const toEnd=top<=0;
  jump.dataset.direction=toEnd?'end':'start';
  jump.setAttribute('aria-label',text(toEnd?'Go to end of list':'Go to start of list'));
  jump.title=text(toEnd?'Go to end of list':'Go to start of list');
  jump.querySelector('path').setAttribute('d',toEnd?'m6 10 6 6 6-6':'m6 14 6-6 6 6');
 }
 function cancel(){
  const previous=hold;hold=null;
  if(previous&&thumb.hasPointerCapture(previous.id)){try{thumb.releasePointerCapture(previous.id);}catch(_){}}
  thumb.classList.remove('dragging');position.hidden=true;hideLater();
 }
 function suspend(){pointers.clear();cancel();}
 function refresh(){
  frame=0;
  const doc=page(),nextViewport=doc.clientHeight,nextWidth=doc.clientWidth;
  const nextMaximum=Math.max(0,doc.scrollHeight-nextViewport);
  if(nav)rail.style.bottom=Math.max(15,root.innerHeight-nav.getBoundingClientRect().top+12)+'px';
  const available=accounts&&nextMaximum>0&&!locked()&&nav&&
   nav.getBoundingClientRect().top-12-parseFloat(getComputedStyle(rail).top)>=176;
  rail.hidden=!available;
  const nextHeight=rail.hidden?0:track.clientHeight;
  if(nextMaximum!==maximum||nextViewport!==viewport||nextWidth!==viewportWidth||nextHeight!==trackHeight)cancel();
  maximum=nextMaximum;viewport=nextViewport;viewportWidth=nextWidth;trackHeight=nextHeight;
  if(rail.hidden){cancel();return;}
  const top=clamp(doc.scrollTop),ratio=maximum>0?top/maximum:0;
  const proportional=trackHeight*viewport/Math.max(1,doc.scrollHeight);
  const visualHeight=Math.max(44,Math.min(88,proportional));
  const hitHeight=Math.max(56,visualHeight);
  travel=Math.max(0,trackHeight-hitHeight);
  thumb.style.height=hitHeight+'px';thumb.style.top=ratio*travel+'px';
  mark.style.height=visualHeight+'px';mark.style.top=((hitHeight-visualHeight)/2)+'px';
  thumb.setAttribute('aria-valuemin','0');thumb.setAttribute('aria-valuemax',String(maximum));
  thumb.setAttribute('aria-valuenow',String(Math.round(top)));
  const percent=Math.round(ratio*100);
  thumb.setAttribute('aria-valuetext',text('List position: {percent}%',{percent}));
  position.textContent=percent+'%';
  position.style.top=Math.max(0,ratio*travel+(hitHeight-28)/2)+'px';
  updateJump(top);
 }
 function schedule(){if(!frame)frame=root.requestAnimationFrame(refresh);}
 function move(value){if(rail.hidden||locked())return;page().scrollTo({top:clamp(value),behavior:'instant'});schedule();}
 jump.addEventListener('click',()=>{
  if(rail.hidden||locked())return;
  cancel();const target=page().scrollTop<=0?maximum:0;wake();
  page().scrollTo({top:target,behavior:reduced()?'instant':'smooth'});schedule();
 });
 thumb.addEventListener('keydown',event=>{
  const top=page().scrollTop,step=65;
  const pageStep=Math.max(48,viewport-(nav?nav.getBoundingClientRect().height:0));
  let target;
  if(event.key==='Home')target=0;else if(event.key==='End')target=maximum;
  else if(event.key==='ArrowUp'||event.key==='ArrowLeft')target=top-step;
  else if(event.key==='ArrowDown'||event.key==='ArrowRight')target=top+step;
  else if(event.key==='PageUp')target=top-pageStep;
  else if(event.key==='PageDown')target=top+pageStep;
  else if(event.key===' ')target=top+(event.shiftKey?-pageStep:pageStep);
  else return;
  event.preventDefault();keyboard=true;cancel();wake();move(target);
 });
 document.addEventListener('pointerdown',event=>{
  keyboard=false;pointers.add(event.pointerId);
  if(pointers.size>1||!event.isPrimary)cancel();
  if(rail.contains(event.target)&&!locked())wake();
 },true);
 thumb.addEventListener('pointerdown',event=>{
  if(event.button!==0||!event.isPrimary||pointers.size!==1||rail.hidden||locked()||travel<=0)return;
  event.preventDefault();cancel();wake();thumb.focus({preventScroll:true});
  hold={id:event.pointerId,anchorY:event.clientY,anchorTop:page().scrollTop};
  thumb.classList.add('dragging');position.hidden=false;
  if(event.isTrusted)thumb.setPointerCapture(event.pointerId);
  schedule();
 });
 document.addEventListener('pointermove',event=>{
  if(!hold||event.pointerId!==hold.id)return;
  event.preventDefault();move(hold.anchorTop+(event.clientY-hold.anchorY)*maximum/travel);
  position.hidden=false;
 },{passive:false});
 function release(event){pointers.delete(event.pointerId);if(hold&&hold.id===event.pointerId)cancel();}
 document.addEventListener('pointerup',release);document.addEventListener('pointercancel',release);
 thumb.addEventListener('lostpointercapture',()=>{if(hold)cancel();});
 thumb.addEventListener('contextmenu',event=>event.preventDefault());
 rail.addEventListener('focusin',wake);rail.addEventListener('focusout',()=>queueMicrotask(hideLater));
 rail.addEventListener('pointerenter',wake);
 root.addEventListener('blur',suspend);root.addEventListener('pagehide',suspend);
 document.addEventListener('visibilitychange',()=>{if(document.hidden)suspend();});
 root.addEventListener('scroll',schedule,{passive:true});
 root.addEventListener('resize',()=>{cancel();schedule();},{passive:true});
 root.visualViewport?.addEventListener('resize',()=>{cancel();schedule();},{passive:true});
 new ResizeObserver(schedule).observe(app);new ResizeObserver(schedule).observe(nav);
 new MutationObserver(()=>{if(locked())suspend();schedule();})
  .observe(document.body,{attributes:true,attributeFilter:['class']});
 return {contentChanged(hasAccounts){cancel();accounts=hasAccounts;rail.classList.add('idle');refresh();},cancel:suspend,refresh:schedule};
};
})(window);
''', encoding="utf-8")

# Scoped dark compact design for About, Settings, Fetcher only.
css = ROOT / "web/style.css"
c = css.read_text(encoding="utf-8")
c += r"""

/* INSFAV Ultra: Builder-inspired design language, scoped to the three requested screens. */
:root{--ultra-bg:#000;--ultra-surface:#090909;--ultra-control:#111;--ultra-deep:#050505;--ultra-border:#303030;--ultra-text:#f1f1f1;--ultra-muted:#888}
:is(#settings,#features-screen,#fetcher-screen){background:var(--ultra-bg);color:var(--ultra-text);font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
:is(#settings,#features-screen,#fetcher-screen) header{background:#000;border-bottom:1px solid #1d1d1d}
:is(#settings,#features-screen,#fetcher-screen) .screen-content{padding:12px 14px max(28px,env(safe-area-inset-bottom))}
:is(#settings,#features-screen,#fetcher-screen) h2{font-size:18px;letter-spacing:-.25px}
:is(#settings,#features-screen,#fetcher-screen) h3{font-size:15px;letter-spacing:.01em;text-transform:none;color:#ddd;margin:18px 2px 10px}
:is(#settings,#features-screen,#fetcher-screen) .muted,:is(#settings,#features-screen,#fetcher-screen) small{color:#858585}
:is(#settings,#features-screen,#fetcher-screen) .action-list,:is(#settings,#features-screen,#fetcher-screen) details,:is(#settings,#features-screen,#fetcher-screen) .features,:is(#settings,#features-screen,#fetcher-screen) .progress-card{background:var(--ultra-deep);border:1px solid var(--ultra-border);border-radius:20px}
#fetcher-screen .metric{background:#050505;border:1px solid #303030;border-radius:20px;padding:12px}
#fetcher-screen .metric b{font-size:18px;color:#f5f5f5}
#fetcher-screen .metric span{font-size:11px;color:#888}
:is(#settings,#features-screen,#fetcher-screen) .action-list{overflow:hidden}
:is(#settings,#features-screen,#fetcher-screen) .action-list button{min-height:48px;padding:12px 14px;color:#e5e5e5;background:#050505;border-bottom:1px solid #252525;font-size:13px;text-align:left}
:is(#settings,#features-screen,#fetcher-screen) .action-list button:last-child{border-bottom:0}
:is(#settings,#features-screen,#fetcher-screen) input:not([type=checkbox]):not([type=radio]),:is(#settings,#features-screen,#fetcher-screen) select,:is(#settings,#features-screen,#fetcher-screen) textarea{min-height:44px;background:#050505;color:#eee;border:1px solid #303030;border-radius:12px;font:13px system-ui,-apple-system,"Segoe UI",sans-serif}
:is(#settings,#features-screen,#fetcher-screen) .choice-trigger,:is(#settings,#features-screen,#fetcher-screen) .btn{min-height:44px;background:#101010;color:#eee;border:1px solid #3a3a3a;border-radius:12px}
:is(#settings,#features-screen,#fetcher-screen) .choice-list button[aria-checked="true"],:is(#settings,#features-screen,#fetcher-screen) button[aria-pressed="true"]{background:#191919;border-color:#666;color:#fff}
:is(#settings,#features-screen,#fetcher-screen) button:focus-visible,:is(#settings,#features-screen,#fetcher-screen) input:focus-visible,:is(#settings,#features-screen,#fetcher-screen) select:focus-visible,:is(#settings,#features-screen,#fetcher-screen) textarea:focus-visible{outline:2px solid #d0d0d0;outline-offset:2px}
#features-screen #features-list{border-radius:20px;border-color:#303030;background:#050505}
#features-screen #features-list li{padding:13px 15px;border-color:#252525;font-size:13px}
#settings #advanced-settings{padding:12px;background:#050505}
#settings .fetcher-toggle{min-height:48px;border-color:#292929}
#fetcher-screen #cookie-text{background:#050505;border-color:#303030;border-radius:12px}
#fetcher-screen .fetcher-fields{gap:10px}
#fetcher-screen .fetcher-inline{gap:8px;flex-wrap:wrap}
#fetcher-screen .fetcher-inline .btn{min-height:44px;letter-spacing:0}
#fetcher-screen .fetcher-toggle{padding:12px 2px}
#fetcher-screen .metrics{gap:8px}
#fetcher-screen .progress-card{padding:12px}
#fetcher-screen #fetcher-process{background:#050505;border:1px solid #303030;border-radius:16px}
#fetcher-screen button.danger,#fetcher-screen .btn.danger{background:#1b0d0d;border-color:#5a3030;color:#f0cccc}
@media(max-width:360px){:is(#settings,#features-screen,#fetcher-screen) .screen-content{padding-inline:11px}#fetcher-screen .fetcher-fields{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}
@media(prefers-reduced-motion:reduce){:is(#settings,#features-screen,#fetcher-screen) *{scroll-behavior:auto!important;animation-duration:.01ms!important;transition-duration:.01ms!important}}

/* One contextual quick-jump; the touch target and proportional handle never reserve list width. */
#main-scroll{z-index:9999}
#scroll-jump{order:2;min-width:52px;min-height:52px;position:relative;z-index:2}
#main-scroll.idle #scroll-jump{pointer-events:auto!important}
#scroll-jump svg{transition:transform 180ms var(--motion-ease),opacity 140ms ease}
#scroll-jump[data-direction="start"] svg{transform:rotate(180deg)}
#scroll-position{position:absolute;right:58px;z-index:3;min-width:54px;padding:5px 8px;border:1px solid #383838;border-radius:10px;background:#111;color:#eee;font:11px system-ui,sans-serif;text-align:center;pointer-events:none}
#scroll-thumb>span{width:40px;max-width:40px;border-radius:999px}
#scroll-thumb.dragging{box-shadow:0 0 12px 2px #7777}
#scroll-thumb.dragging>span{background:rgba(145,145,145,.27);border-color:#555}
#scroll-thumb:focus-visible{outline:2px solid #ddd;outline-offset:-2px}
@media(prefers-reduced-motion:reduce){#scroll-jump svg,#scroll-thumb,#scroll-thumb>span{transition:none!important}}
"""
css.write_text(c, encoding="utf-8")

# New automated browser tests for the contextual control and immediate drag interaction.
test_scroll = r'''\'use strict\';
const assert=require('node:assert/strict'),fs=require('node:fs'),http=require('node:http'),path=require('node:path');
const {chromium}=require('playwright');
(async()=>{
 const root=path.resolve(__dirname,'../app/src/main/assets');
 const server=http.createServer((req,res)=>{
  if(req.url.startsWith('/thumb/')){res.setHeader('Content-Type','image/svg+xml');res.end('<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60"><rect width="60" height="60" fill="#444"/></svg>');return;}
  const file=path.resolve(root,'.'+(req.url==='/'?'/index.html':req.url.split('?')[0]));
  if(!file.startsWith(root+path.sep)||!fs.existsSync(file)){res.writeHead(404).end();return;}
  res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':file.endsWith('.woff2')?'font/woff2':file.endsWith('.jpg')?'image/jpeg':'text/html');res.end(fs.readFileSync(file));
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({executablePath:process.env.CHROME_BIN,args:['--no-sandbox','--disable-gpu']});
 let checks=0;const check=(v,m)=>{assert.ok(v,m);checks++;};
 const settled=page=>page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 async function create(count){
  const page=await browser.newPage({viewport:{width:393,height:850},hasTouch:true,reducedMotion:'reduce'});
  page.on('pageerror',e=>{throw e;});
  await page.addInitScript(n=>{
   const items=Array.from({length:n},(_,i)=>({pageId:'account_'+i,name:'Account '+i}));
   window.fixture=JSON.stringify([{name:'First',items:items.slice(0,n/2)},{name:'Second',items:items.slice(n/2)}]);
   window.Android={request(raw){const q=JSON.parse(raw);if(q.command==='bootstrap')nativeEvent('bootstrap',{raw:fixture,profiles:{},language:'en'});}};
  },count);
  await page.goto('http://127.0.0.1:'+server.address().port);
  await page.locator('#splash').waitFor({state:'hidden'});await settled(page);return page;
 }
 async function expand(page){await page.locator('.folder-header').nth(1).click();await page.locator('.folder-header').first().click();await settled(page);}
 async function metrics(page){return page.evaluate(()=>{
  const doc=document.scrollingElement,t=document.querySelector('#scroll-track'),h=document.querySelector('#scroll-thumb');
  return {top:doc.scrollTop,max:doc.scrollHeight-doc.clientHeight,track:t.clientHeight,hit:h.clientHeight,
   offset:parseFloat(h.style.top),height:parseFloat(h.firstElementChild.style.height),
   now:+h.getAttribute('aria-valuenow'),maxAria:+h.getAttribute('aria-valuemax'),
   active:h.classList.contains('dragging'),positionHidden:document.querySelector('#scroll-position').hidden};
 });}
 try{
  for(const count of [100,1000,10000,15000,20000]){
   const page=await create(count),rail=page.locator('#main-scroll');
   check(await rail.isHidden(),'Closed '+count+' rows keep scrollbar hidden');
   await expand(page);check(await rail.isVisible(),'Expanded '+count+' rows reveal controller');
   check(await page.locator('#scroll-jump').count()===1,'Exactly one quick-jump button is present');
   check(await page.locator('#scroll-start,#scroll-end').count()===0,'Paired controls are removed');
   let m=await metrics(page);
   check(m.max>0&&m.top===0&&m.now===0&&m.maxAria===m.max,'Initial thumb and ARIA reflect actual document bounds');
   check(await page.locator('#scroll-jump').getAttribute('aria-label')==='Go to end of list','At top the control offers jump to end');
   await page.locator('#scroll-jump').tap();await page.waitForFunction(()=>document.scrollingElement.scrollTop===document.scrollingElement.scrollHeight-document.scrollingElement.clientHeight);await settled(page);
   m=await metrics(page);check(m.top===m.max&&m.now===m.max,'Quick-jump reaches exact document end');
   check(await page.locator('#scroll-jump').getAttribute('aria-label')==='Go to start of list','Away from top the control offers jump to beginning');
   await page.locator('#scroll-jump').tap();await page.waitForFunction(()=>document.scrollingElement.scrollTop===0);await settled(page);
   check((await metrics(page)).top===0,'Quick-jump returns to exact document beginning');
   await page.evaluate(()=>scrollTo(0,(document.scrollingElement.scrollHeight-innerHeight)/2));await settled(page);m=await metrics(page);
   check(Math.abs(m.offset-(m.track-m.hit)*m.top/m.max)<1,'Thumb position follows actual scroll ratio');
   check(m.height>=44&&m.hit>=56,'Visual handle and touch target meet minimum sizes');
   const thumb=page.locator('#scroll-thumb'),box=await thumb.boundingBox();
   await thumb.dispatchEvent('pointerdown',{pointerId:1,pointerType:'touch',isPrimary:true,button:0,clientX:box.x+24,clientY:box.y+box.height/2});
   check((await metrics(page)).active,'Dragging activates immediately without a hold delay');
   check(!(await metrics(page)).positionHidden,'Percentage appears during active drag');
   const before=await metrics(page);
   await thumb.dispatchEvent('pointermove',{pointerId:1,pointerType:'touch',isPrimary:true,clientX:box.x+24,clientY:box.y+before.track/2});
   await settled(page);m=await metrics(page);
   check(m.top>before.top&&m.now===m.top,'Finger movement updates document position and ARIA continuously');
   await thumb.dispatchEvent('pointercancel',{pointerId:1,pointerType:'touch',isPrimary:true});await settled(page);
   check(!(await metrics(page)).active&&(await metrics(page)).positionHidden,'Pointer cancellation clears drag and indicator');
   await thumb.focus();await page.keyboard.press('Home');await settled(page);check((await metrics(page)).top===0,'Home reaches start');
   await page.keyboard.press('End');await settled(page);check((await metrics(page)).top===(await metrics(page)).max,'End reaches exact end');
   await page.keyboard.press('PageUp');await settled(page);check((await metrics(page)).top<(await metrics(page)).max,'PageUp moves by a viewport');
   await page.locator('#search-input').fill('account_'+(count-1));await page.waitForTimeout(200);await settled(page);
   check(await rail.isHidden(),'Single-row filtered result hides controller');
   await page.locator('#search-input').fill('account_');await page.waitForTimeout(200);await settled(page);
   check(await rail.isVisible(),'Clearing search restores scrollbar geometry');
   await page.setViewportSize({width:320,height:480});await settled(page);
   check((await metrics(page)).max>0,'Portrait resize retains scroll range');
   await page.setViewportSize({width:850,height:393});await settled(page);
   check((await metrics(page)).max>0,'Landscape resize retains scroll range');
   await page.close();
  }
  const page=await create(5000);await expand(page);
  await page.evaluate(()=>document.body.classList.add('overlay-open'));await settled(page);
  check(await page.locator('#main-scroll').isHidden(),'Modal overlay hides controller');
  await page.evaluate(()=>document.body.classList.remove('overlay-open'));await settled(page);
  check(await page.locator('#main-scroll').isVisible(),'Closing overlay restores controller');
  await page.emulateMedia({reducedMotion:'reduce'});
  const start=Date.now();await page.locator('#scroll-jump').tap();
  await page.waitForFunction(()=>document.scrollingElement.scrollTop===document.scrollingElement.scrollHeight-document.scrollingElement.clientHeight);
  check(Date.now()-start<1000,'Reduced motion uses immediate quick-jump');
  await page.close();
  console.log('PASS '+checks+' Ultra scroll checks: 100–20000 rows, single contextual jump, immediate drag, proportional handle, percentage, cancellation, keyboard, search, resize, overlays and reduced motion');
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exitCode=1;});
'''
test_scroll = test_scroll.replace("\\'", "'")
(ROOT / "tests/list-scroll.cjs").write_text(test_scroll, encoding="utf-8")

with (ROOT / "PERFORMANCE.md").open("a", encoding="utf-8") as f:
    f.write("""
\n## Ultra bootstrap baseline and Rust decision\n\nThe tables above are inherited, unchanged evidence from pinned Plus source commit 356ba98a7ab479caf1b64526133f05944ce17efc; they are not measurements performed on Ultra. Ultra keeps the Java production path enabled by default. The isolated Rust parser/JNI prototype is opt-in with -PultraNativeCore=true, targets arm64-v8a, armeabi-v7a, and x86_64, and must not be enabled by default until same-runner Java/JNI medians show a repeatable improvement of at least 15% with no correctness, memory, startup, APK-size, or regression issue. Instrumentation emits raw 1k/10k/15k results for review. No Rust performance win is claimed in this bootstrap change.\n""")

# Android 13+ hides app notifications until POST_NOTIFICATIONS is granted.
# The foreground service test explicitly grants this permission before checking its ongoing card.
pool_test = ROOT / "app/src/androidTest/java/com/instagram/insfav/fetcher/PoolInstrumentation.java"
pool_text = pool_test.read_text(encoding="utf-8")
native_matrix_start = "      com.instagram.insfav.RescanDeviceBenchmark.run(this);"
assert pool_text.count(native_matrix_start) == 1, "Expected one custom instrumentation entry point"
native_matrix = """      com.instagram.insfav.NativeCoreInstrumentationTest nativeCore =
          new com.instagram.insfav.NativeCoreInstrumentationTest();
      nativeCore.nativeAndJavaAreEquivalentAcrossRequiredCases();
      sendStatus(0, status("ULTRA_NATIVE_JNI_EQUIVALENCE_OK"));
      nativeCore.benchmarkJavaAgainstRustAndEmitRawResults();
"""
pool_text = pool_text.replace(native_matrix_start, native_matrix + native_matrix_start, 1)
pool_launch = '    FetchService.request(c, "missing");'
assert pool_text.count(pool_launch) == 1, "Expected one foreground-service instrumentation launch"
pool_grant = """      if (Build.VERSION.SDK_INT >= 33) {
        getUiAutomation().grantRuntimePermission(
            c.getPackageName(), android.Manifest.permission.POST_NOTIFICATIONS);
        if (c.checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
            != android.content.pm.PackageManager.PERMISSION_GRANTED)
          throw new AssertionError("POST_NOTIFICATIONS runtime permission was not granted to Ultra");
      }
"""
pool_test.write_text(pool_text.replace(pool_launch, pool_grant + pool_launch, 1), encoding="utf-8")

# The one-shot workflow is not part of the final repository tree.
bootstrap_workflow = ROOT / ".github/workflows/ultra-bootstrap.yml"
if bootstrap_workflow.exists(): bootstrap_workflow.unlink()

# Keep release defaults independent of the Plus release train.
for path in ROOT.rglob("*"):
    if path.is_file() and path.suffix.lower() in extensions:
        try: value = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError): continue
        value = value.replace("1.1.16", "1.0.0").replace("'22'", "'1'").replace('"22"', '"1')
        path.write_text(value, encoding="utf-8")

print("Ultra source bootstrap and scoped feature changes staged; pinned Plus source SHA:", PLUS_SHA)
