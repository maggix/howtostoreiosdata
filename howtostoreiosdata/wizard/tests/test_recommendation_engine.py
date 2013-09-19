from django.test import TestCase
from howtostoreiosdata.wizard.recommendation import RecommendationEngine


class RecommendationEngineTest(TestCase):
    def test_storage_core_data(self):
        self._test_storage(RecommendationEngine.STORAGE_CORE_DATA, 'NSFileProtectionComplete')

    def test_storage_sql(self):
        self._test_storage(RecommendationEngine.STORAGE_SQL, 'SQLITE_OPEN_FILEPROTECTION_COMPLETE')

    def test_storage_raw_data(self):
        self._test_storage(RecommendationEngine.STORAGE_RAW_DATA, 'NSDataWritingFileProtectionComplete')

    def test_storage_keychain(self):
        self._test_storage(RecommendationEngine.STORAGE_KEYCHAIN, 'kSecAttrAccessibleWhenUnlocked')

    def test_storage_defaults(self):
        r = RecommendationEngine(RecommendationEngine.STORAGE_DEFAULTS, RecommendationEngine.BACKGROUND_NONE)
        self.assertEqual(r.storage, RecommendationEngine.STORAGE_KEYCHAIN)

    def _test_storage(self, storage, protection_level_name):
        r = RecommendationEngine(storage, RecommendationEngine.BACKGROUND_NONE)
        self.assertEqual(r.storage, storage)
        self.assertEqual(r.protection_level, RecommendationEngine.PROTECTION_LEVEL_ALWAYS)
        self.assertEqual(r.protection_level_full_name(), protection_level_name)
        self.assertTrue(r.protection_level_explanation())
        self.assertTrue(protection_level_name in r.code_sample())

    def test_uses_unlessopen_correctly(self):
        r = RecommendationEngine(RecommendationEngine.STORAGE_RAW_DATA, RecommendationEngine.BACKGROUND_OPEN_ONLY)
        self.assertEqual(r.protection_level, RecommendationEngine.PROTECTION_LEVEL_UNLESS_OPEN)

        # In Keychain, there is no such protection level, so default to normal backgrounding.
        r = RecommendationEngine(RecommendationEngine.STORAGE_KEYCHAIN, RecommendationEngine.BACKGROUND_OPEN_ONLY)
        self.assertEqual(r.protection_level, RecommendationEngine.PROTECTION_LEVEL_AFTER_FIRST_UNLOCK)

    def test_forces_keychain_with_sharing(self):
        r = RecommendationEngine(RecommendationEngine.STORAGE_RAW_DATA, RecommendationEngine.BACKGROUND_OPEN_ONLY, True)
        self.assertEqual(r.storage, RecommendationEngine.STORAGE_KEYCHAIN)

    def test_background_protection_level(self):
        r = RecommendationEngine(RecommendationEngine.STORAGE_RAW_DATA, RecommendationEngine.BACKGROUND_ALWAYS)
        self.assertEqual(r.protection_level, RecommendationEngine.PROTECTION_LEVEL_AFTER_FIRST_UNLOCK)
