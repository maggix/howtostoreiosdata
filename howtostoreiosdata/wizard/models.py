
# Note that this is not a Django database model.


class RecommendationEngine(object):
    # This is 'Always' from the NSFileManager/NSData perspective, where always means "always protect".
    PROTECTION_LEVEL_ALWAYS = 'always'
    PROTECTION_LEVEL_AFTER_FIRST_UNLOCK = 'after_first_unlock'
    PROTECTION_LEVEL_UNLESS_OPEN = 'unless_open'
    
    STORAGE_CORE_DATA = 'Core Data'
    STORAGE_DEFAULTS = 'NSUserDefaults'
    STORAGE_SQL = 'raw SQLite'
    STORAGE_RAW_DATA = 'raw NSData'
    STORAGE_KEYCHAIN = 'Keychain'

    BACKGROUND_NONE = 'NO'
    BACKGROUND_OPEN_ONLY = 'OPEN_ONLY'
    BACKGROUND_ALWAYS = 'YES'

    PROTECTION_LEVEL_EXPLANATION = {
        PROTECTION_LEVEL_ALWAYS:
            """With this protection level, the data is only available while the device is unlocked. As soon as the
            device is locked, you can no longer access the data. This is the most secure level, but does not allow
            you to perform background tasks.""",
        PROTECTION_LEVEL_AFTER_FIRST_UNLOCK:
            """With this protection level, the data is only available after the device has been unlocked at least once.
            This means your app can access this data in the background, but if the device reboots, perhaps to let
            someone install a jailbreak, the data is no longer accessible.""",
        PROTECTION_LEVEL_UNLESS_OPEN:
            """With this protection level, the data is only available while the device is unlocked. If the
            device is locked while you still have the file opened, you can continue reading and writing, but once
            closed, you can no longer open the file."""
    }

    STORAGE_CODE_SAMPLE = {
        STORAGE_CORE_DATA: """- (NSPersistentStoreCoordinator *)persistentStoreCoordinator {
  if (persistentStoreCoordinator_ != nil) {
    return persistentStoreCoordinator_;
  }

  persistentStoreCoordinator_ = [[NSPersistentStoreCoordinator alloc]
                        initWithManagedObjectModel:[self managedObjectModel]];

  NSURL *storeURL = [NSURL fileURLWithPath:
        [[self applicationDocumentsDirectory] stringByAppendingPathComponent: @"MyStore.sqlite"]];

  [persistentStoreCoordinator_ addPersistentStoreWithType:NSSQLiteStoreType
                     configuration:nil URL:storeURL options:nil error:&error]);

  NSDictionary *fileAttributes = [NSDictionary
                 dictionaryWithObject:%s
                 forKey:NSFileProtectionKey];
  [[NSFileManager defaultManager] setAttributes:fileAttributes
                      ofItemAtPath:[storeURL path] error: &error]);

  return persistentStoreCoordinator_;
}""",
        STORAGE_SQL: """int flags = SQLITE_OPEN_CREATE |
            SQLITE_OPEN_READWRITE |
            %s;

sqlite3_open_v2(path, &database, flags, NULL)

// Or, if you prefer FMDB:
FMDatabase *database = [FMDatabase databaseWithPath:dbPath];
[database openWithFlags:flags]""",


        STORAGE_RAW_DATA: """NSData *contents = [@"secret file contents" dataUsingEncoding:NSUTF8StringEncoding];

[contents writeToFile:path
          options:%s
            error:&error];""",


        STORAGE_KEYCHAIN: """NSString *account = @"username";
NSString *password = @"password";

NSMutableDictionary *item = [NSMutableDictionary dictionary];

// Note that metadata, like the account name, is not encrypted.
[item setObject:account
          forKey:(id)kSecAttrAccount];

[item setObject:(id)kSecClassGenericPassword
          forKey:(id)kSecClass];

[item setObject:(id)%s
          forKey:(id)kSecAttrAccessible];

[item setObject:[password dataUsingEncoding:NSUTF8StringEncoding]
          forKey:(id)kSecValueData];

OSStatus error = SecItemAdd((CFDictionaryRef)item, NULL);""",
    }


    PROTECTION_LEVEL_FULL_NAME = {
        STORAGE_CORE_DATA: {
            PROTECTION_LEVEL_ALWAYS: 'NSFileProtectionComplete',
            PROTECTION_LEVEL_AFTER_FIRST_UNLOCK: 'NSFileProtectionCompleteUntilFirstUserAuthentication',
            PROTECTION_LEVEL_UNLESS_OPEN: 'NSFileProtectionCompleteUnlessOpen',
        },
        STORAGE_SQL: {
            PROTECTION_LEVEL_ALWAYS: 'SQLITE_OPEN_FILEPROTECTION_COMPLETE',
            PROTECTION_LEVEL_AFTER_FIRST_UNLOCK: 'SQLITE_OPEN_FILEPROTECTION_COMPLETEUNTILFIRSTUSERAUTHENTICATION',
            PROTECTION_LEVEL_UNLESS_OPEN: 'SQLITE_OPEN_FILEPROTECTION_COMPLETEUNLESSOPEN',
        },
        STORAGE_RAW_DATA: {
            PROTECTION_LEVEL_ALWAYS: 'NSDataWritingFileProtectionComplete',
            PROTECTION_LEVEL_AFTER_FIRST_UNLOCK: 'NSDataWritingFileProtectionCompleteUntilFirstUserAuthentication',
            PROTECTION_LEVEL_UNLESS_OPEN: 'NSDataWritingFileProtectionCompleteUnlessOpen',
        },
        STORAGE_KEYCHAIN: {
            PROTECTION_LEVEL_ALWAYS: 'kSecAttrAccessibleWhenUnlocked',
            PROTECTION_LEVEL_AFTER_FIRST_UNLOCK: 'kSecAttrAccessibleAfterFirstUnlock',
        },
    }


    def __init__(self, storage, background, sharing):
        self.sharing = sharing
        self.background = background
        self.storage = self._recommended_storage(storage, sharing)
        self.protection_level = self._recommended_protection_level(self.background, self.storage)

    def _recommended_storage(self, storage, sharing):
        if (storage == RecommendationEngine.STORAGE_DEFAULTS) or sharing:
            return RecommendationEngine.STORAGE_KEYCHAIN
        return storage

    def _recommended_protection_level(self, background, storage):
        if background == RecommendationEngine.BACKGROUND_ALWAYS:
            return RecommendationEngine.PROTECTION_LEVEL_AFTER_FIRST_UNLOCK
        if background == RecommendationEngine.BACKGROUND_NONE:
            return RecommendationEngine.PROTECTION_LEVEL_ALWAYS

        if background == RecommendationEngine.BACKGROUND_OPEN_ONLY:
            if storage == RecommendationEngine.STORAGE_KEYCHAIN:
                return RecommendationEngine.PROTECTION_LEVEL_AFTER_FIRST_UNLOCK
            else:
                return RecommendationEngine.PROTECTION_LEVEL_UNLESS_OPEN

    def protection_level_explanation(self):
        return self.PROTECTION_LEVEL_EXPLANATION[self.protection_level]

    def code_sample(self):
        return self.STORAGE_CODE_SAMPLE[self.storage] % self.protection_level_full_name()

    def protection_level_full_name(self):
        return self.PROTECTION_LEVEL_FULL_NAME[self.storage][self.protection_level]

