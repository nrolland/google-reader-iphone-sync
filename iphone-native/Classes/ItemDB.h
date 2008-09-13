#import <Foundation/Foundation.h>
#import "FMDatabase.h"
#import "FMDatabaseAdditions.h"
#import "FeedItem.h"

@interface ItemDB : NSObject {
	FMDatabase* db;
	NSString * filename;
}
-(void) load;
-(void) updateItem: (id) item;

- (NSEnumerator *) allItems;
- (NSEnumerator *) unreadItems;
- (NSEnumerator *) readItems;
- (NSEnumerator *) starredItems;
- (NSEnumerator *) locallyModifiedItems;

- (id) itemWithID: (NSString *) google_id;

@end

