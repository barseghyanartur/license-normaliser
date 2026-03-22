"""Tests for _cache.py - thread-safe default normaliser singleton."""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor

from license_normaliser._cache import (
    _DefaultNormaliser,
    get_registry_keys,
    normalise_license,
    normalise_licenses,
)
from license_normaliser._normaliser import LicenseNormaliser


class TestDefaultNormaliserSingleton:
    def test_singleton_instance_reused(self) -> None:
        d1 = _DefaultNormaliser()
        d2 = _DefaultNormaliser()
        assert d1.get() is d2.get()

    def test_get_returns_license_normaliser(self) -> None:
        d = _DefaultNormaliser()
        instance = d.get()
        assert isinstance(instance, LicenseNormaliser)

    def test_thread_safety_same_instance(self) -> None:
        results: list[object | None] = [None] * 20
        errors: list[BaseException | None] = [None] * 20

        def get_instance(idx: int) -> None:
            try:
                d = _DefaultNormaliser()
                results[idx] = d.get()
            except BaseException as e:  # noqa: BLE001
                errors[idx] = e

        threads = [threading.Thread(target=get_instance, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(e is None for e in errors)
        assert results[0] is not None
        assert all(r is results[0] for r in results if r is not None)

    def test_concurrent_normalise_license(self) -> None:
        licenses = ["MIT", "Apache-2.0", "CC BY 4.0", "GPL-3.0", "BSD-3-Clause"]
        results: list[str] = []

        def normalise(lic: str) -> None:
            v = normalise_license(lic)
            results.append(v.key)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(normalise, lic) for lic in licenses * 4]
            for f in futures:
                f.result(timeout=5)

        assert len(results) == len(licenses) * 4
        assert set(results) == {
            "mit",
            "apache-2.0",
            "cc-by-4.0",
            "gpl-3.0",
            "bsd-3-clause",
        }


class TestModuleLevelAPI:
    def test_normalise_license_returns_license_version(self) -> None:
        v = normalise_license("MIT")
        assert str(v) == "mit"

    def test_normalise_licenses_returns_list(self) -> None:
        results = normalise_licenses(["MIT", "Apache-2.0"])
        assert len(results) == 2
        assert all(str(r) in ("mit", "apache-2.0") for r in results)

    def test_get_registry_keys_returns_set_of_strings(self) -> None:
        keys = get_registry_keys()
        assert isinstance(keys, set)
        assert len(keys) > 1000
        assert "mit" in keys
        assert "apache-2.0" in keys
