from django.db import models
from django_extensions.db.models import TimeStampedModel
from model_utils import Choices

# This is a horrible misuse of Django models - this data is never stored in the DB.
# Also, the code looks like crap, so it really needs to be refactored into a better structure.


class Recommendation(TimeStampedModel):
    PROTECTION_LEVEL = Choices('after_first_unlock', 'always', 'unless_open')
    STORAGE = Choices(
        ('core_data', 'Core Data'),
        ('defaults', 'NSUserDefaults'),
        ('rawsql', 'Raw SQLite'),
        ('raw_data', 'Raw NSdata'),
        ('keychain', 'Keychain')
    )

    PROTECTION_LEVEL_EXPLANATION = {
        PROTECTION_LEVEL.always:
            """With this protection level, the data is only available while the device is unlocked. As soon as the
            device is locked, you can no longer access the data. This is the most secure level, but does not allow
            you to perform background tasks.""",
        PROTECTION_LEVEL.after_first_unlock:
            """With this protection level, the data is only available after the device has been unlocked at least once.
            This means your app can access this data in the background, but if the device reboots, perhaps to let
            someone install a jailbreak, the data is no longer accessible.""",
        PROTECTION_LEVEL.unless_open:
            """With this protection level, the data is only available while the device is unlocked. If the
            device is locked while you still have the file opened, you can continue reading and writing, but once
            closed, you can no longer open the file."""
    }

    STORAGE_CODE_SAMPLE = {
        STORAGE.core_data: """- (NSPersistentStoreCoordinator *)persistentStoreCoordinator {
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
        STORAGE.rawsql: """int flags = SQLITE_OPEN_CREATE |
            SQLITE_OPEN_READWRITE |
            %s;

sqlite3_open_v2(path, &database, flags, NULL)

// Or, if you prefer FMDB:
FMDatabase *database = [FMDatabase databaseWithPath:dbPath];
[database openWithFlags:flags]""",


        STORAGE.raw_data: """NSData *contents =
    [@"secret file contents" dataUsingEncoding:NSUTF8StringEncoding];

[contents writeToFile:path
          options:%s
            error:&error];""",


        STORAGE.keychain: """NSString *account = @"username";
NSString *password = @"password";

NSMutableDictionary *item = [NSMutableDictionary dictionary];

// Note that metadata, like the account name is not encrypted
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
        STORAGE.core_data: {
            PROTECTION_LEVEL.always: 'NSFileProtectionComplete',
            PROTECTION_LEVEL.after_first_unlock: 'NSFileProtectionCompleteUntilFirstUserAuthentication',
            PROTECTION_LEVEL.unless_open: 'NSFileProtectionCompleteUnlessOpen',
        },
        STORAGE.rawsql: {
            PROTECTION_LEVEL.always: 'SQLITE_OPEN_FILEPROTECTION_COMPLETE',
            PROTECTION_LEVEL.after_first_unlock: 'SQLITE_OPEN_FILEPROTECTION_COMPLETEUNTILFIRSTUSERAUTHENTICATION',
            PROTECTION_LEVEL.unless_open: 'SQLITE_OPEN_FILEPROTECTION_COMPLETEUNLESSOPEN',
        },
        STORAGE.raw_data: {
            PROTECTION_LEVEL.always: 'NSDataWritingFileProtectionComplete',
            PROTECTION_LEVEL.after_first_unlock: 'NSDataWritingFileProtectionCompleteUntilFirstUserAuthentication',
            PROTECTION_LEVEL.unless_open: 'NSDataWritingFileProtectionCompleteUnlessOpen',
        },
        STORAGE.keychain: {
            PROTECTION_LEVEL.always: 'kSecAttrAccessibleWhenUnlocked',
            PROTECTION_LEVEL.after_first_unlock: 'kSecAttrAccessibleAfterFirstUnlock',
        },
    }

    protection_level = models.CharField(max_length=255, choices=PROTECTION_LEVEL)
    storage = models.CharField(max_length=255, choices=STORAGE)

    def protection_level_explanation(self):
        return self.PROTECTION_LEVEL_EXPLANATION[self.protection_level]

    def code_sample(self):
        return self.STORAGE_CODE_SAMPLE[self.storage] % self.protection_level_full_name()

    def protection_level_full_name(self):
        return self.PROTECTION_LEVEL_FULL_NAME[self.storage][self.protection_level]