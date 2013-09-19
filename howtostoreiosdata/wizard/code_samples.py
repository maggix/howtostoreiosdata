# All the code samples below have one parameter, which is where the protection level name
# for that storage type will be inserted, e.g. NSDataWritingFileProtectionCompleteUnlessOpen

CODE_SAMPLE_CORE_DATA = """
- (NSPersistentStoreCoordinator *)persistentStoreCoordinator {
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
}"""


CODE_SAMPLE_SQL = """
int flags = SQLITE_OPEN_CREATE |
            SQLITE_OPEN_READWRITE |
            %s;

sqlite3_open_v2(path, &database, flags, NULL)

// Or, if you prefer FMDB:
FMDatabase *database = [FMDatabase databaseWithPath:dbPath];
[database openWithFlags:flags]
"""


CODE_SAMPLE_RAW_DATA = """
NSData *contents = [@"secret file contents" dataUsingEncoding:NSUTF8StringEncoding];

[contents writeToFile:path
          options:%s
            error:&error];
"""


CODE_SAMPLE_KEYCHAIN = """
NSString *account = @"username";
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

OSStatus error = SecItemAdd((CFDictionaryRef)item, NULL);
"""
