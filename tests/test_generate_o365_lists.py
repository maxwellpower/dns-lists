import unittest

from scripts.generate_o365_lists import (
    GITHUB_CORE_EXTRA_DOMAINS,
    MINIMAL_DOMAINS,
    SANE_DOMAINS,
    extract_github_domains,
    extract_last_updated,
    normalise_domain,
    render_allowlist,
    strip_last_updated,
    validate_file_content,
)


class NormaliseDomainTests(unittest.TestCase):
    def test_normalises_leading_wildcards(self):
        self.assertEqual(normalise_domain("*.outlook.com"), "outlook.com")
        self.assertEqual(normalise_domain("*cdn.onenote.net"), "cdn.onenote.net")

    def test_collapses_mid_label_wildcards_to_suffix(self):
        self.assertEqual(normalise_domain("autodiscover.*.onmicrosoft.com"), "onmicrosoft.com")

    def test_rejects_non_domain_values(self):
        self.assertIsNone(normalise_domain("https://outlook.office.com"))
        self.assertIsNone(normalise_domain("13.107.6.152"))
        self.assertIsNone(normalise_domain("not a domain"))


class ValidateFileContentTests(unittest.TestCase):
    def test_validates_curated_files(self):
        minimal = render_allowlist(MINIMAL_DOMAINS, ["header"], "2026-03-15")
        sane = render_allowlist(SANE_DOMAINS, ["header"], "2026-03-15")
        validate_file_content("minimal", minimal, required_domains=MINIMAL_DOMAINS)
        validate_file_content("sane", sane, required_domains=SANE_DOMAINS)

    def test_rejects_duplicates(self):
        with self.assertRaisesRegex(Exception, "duplicate"):
            validate_file_content("full", "! header\n\n@@||a.com^\n@@||a.com^\n")

    def test_rejects_regex_style_entries(self):
        with self.assertRaisesRegex(Exception, "Invalid rule format"):
            validate_file_content("full", "! header\n\n@@||a(b).com^\n")

    def test_last_updated_helpers(self):
        rendered = render_allowlist({"example.com"}, ["header"], "2026-03-15")
        self.assertEqual(extract_last_updated(rendered), "2026-03-15")
        self.assertNotIn("Last Updated", strip_last_updated(rendered))


class GitHubMetaTests(unittest.TestCase):
    def test_extracts_core_domains_from_meta_payload(self):
        payload = {
            "domains": {
                "website": [
                    "*.github.com",
                    "*.github.dev",
                    "*.githubusercontent.com",
                ],
                "actions_inbound": {
                    "full_domains": [
                        "api.github.com",
                        "codeload.github.com",
                        "github-registry-files.githubusercontent.com",
                    ]
                },
            }
        }
        domains = extract_github_domains(payload)
        self.assertIn("github.com", domains)
        self.assertIn("github.dev", domains)
        self.assertIn("githubusercontent.com", domains)
        self.assertIn("api.github.com", domains)
        self.assertIn("codeload.github.com", domains)
        self.assertNotIn("github-registry-files.githubusercontent.com", domains)
        self.assertIn("api.github.com", GITHUB_CORE_EXTRA_DOMAINS)


if __name__ == "__main__":
    unittest.main()
