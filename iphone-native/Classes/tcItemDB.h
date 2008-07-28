#import <Foundation/Foundation.h>
#import "FMDatabase.h"
#import "FMDatabaseAdditions.h"
#import "tcItem.h"

@interface tcItemDB : NSObject {
	FMDatabase* db;
}
-(id) initWithFilename: (NSString *)filename;
-(id) initWithPath:(NSString *) path;
-(void) updateItem: (id) item;

- (NSEnumerator *) allItems;
- (NSEnumerator *) unreadItems;
- (NSEnumerator *) readItems;
- (NSEnumerator *) starredItems;
- (NSEnumerator *) locallyModifiedItems;

- (id) itemWithID: (NSString *) google_id;

@end

