#import <UIKit/UIKit.h>
#import "FMDatabase.h"
#import "FMDatabaseAdditions.h"
#import "TCHelpers.h"
#import "ItemDB.h"
#import "FeedItem.h"
#import "TagItem.h"

@interface FeedItemEnumerator : NSEnumerator {
	FMResultSet* rs;
	ItemDB * db;
	SEL constructor;
}
- (id) initWithResultSet: result_set fromDB:(ItemDB *) the_db;
@end


@implementation ItemDB

NSString * all_items_tag = @"All Items";

#define db_ok [self dbHadError]
#define if_error if([self dbHadError])
- (void) awakeFromNib {
	[self load];
}

-(void) load {
	if(filename == nil){
		filename = @"items.sqlite";
	}
	id appdel = [[UIApplication sharedApplication] delegate];
	id sett = [appdel settings];
	id dp = [sett docsPath];
	NSString *path = [[[[[UIApplication sharedApplication] delegate] settings] docsPath] stringByAppendingPathComponent:filename];
	dbg(@"loading database at path: %@", path);
	db = [[FMDatabase alloc] initWithPath:path];
	if (![db open]) {
		NSLog(@"Could not open db.");
		[db release];
		[[NSException exceptionWithName:@"ItemDBException" reason:@"Couldn't open the DB" userInfo:nil] raise];
		return;
	}
	dbg(@"success!");
}

- (void) dealloc {
	NSLog(@"db is being dealloc'd!");
	[filename release];
	[self close];
	[super dealloc];
}

- (void) close {
	[db close];
	[db release];
}

- (void) reload {
	[self close];
	[self load];
}

- (BOOL) dbHadError {
	if ([db hadError]) {
		NSLog(@"Error %d: %@", [db lastErrorCode], [db lastErrorMessage]);
		return YES;
	}
	return NO;
}
	

- (void) updateItem:(id) item {
	[db executeUpdate:@"update items set is_read=?, is_starred=? , is_dirty=1 where google_id=?" ,
		[NSNumber numberWithBool: [item is_read]],
		[NSNumber numberWithBool: [item is_starred]],
		[item google_id]];
	if_error [NSException raise:@"UpdateFailed" format:@"updating item id %@ failed", [item google_id]];
}

- (id) itemFromResultSet: (FMResultSet *)rs {
	return [[[FeedItem alloc]
			initWithId:		[rs stringForColumn:@"google_id"]
			originalId:		[rs stringForColumn:@"original_id"]
			date:			[rs stringForColumn:@"date"]
			url:			[rs stringForColumn:@"url"]
			title:			[rs stringForColumn:@"title"]
			content:		[rs stringForColumn:@"content"]
			feedName:		[rs stringForColumn:@"feed_name"]
			is_read:		[rs boolForColumn:@"is_read"]
			is_starred:		[rs boolForColumn:@"is_starred"]
			db: self]
		autorelease];
}

- (id) tagItemFromResultSet: (FMResultSet *)rs {
	dbg(@"making a tag item from result set %@", rs);
	return [[[TagItem alloc]
			initWithTag:	[rs stringForColumn:@"feed_name"]
			count:			[rs intForColumn:@"num_items"]
			db: self]
		autorelease];
}


- (NSEnumerator *) enumeratorWithConstructor:(SEL)constructor forQuery: (NSString *) sql arguments: (va_list) args {
	dbg(@"** SQL: enumeratorForQuery: %@, ", sql);
	FMResultSet *rs = [db executeQuery:sql arguments:args];
	if_error return nil;
	
	return [[[FeedItemEnumerator alloc] initWithResultSet:rs fromDB: self withConstructor: constructor] autorelease];
}

- (NSEnumerator *) enumeratorWithConstructor:(SEL)constructor forQuery: (NSString *) sql, ... {
	va_list args;
	va_start(args, sql);

	id ret = [self enumeratorWithConstructor:constructor forQuery: sql arguments: args];
	
	va_end(args);
	return ret;
}

- (NSEnumerator *) itemsMatchingCondition:(NSString *) condition, ... {
	NSString * query = @"select * from items";
	if(condition != nil){
		query = [query stringByAppendingFormat: @" where %@", condition];
	}
	va_list args;
	va_start(args, condition);
	// TODO: better pagination
	id retval = [self enumeratorWithConstructor:@selector(itemFromResultSet:) forQuery: [query stringByAppendingFormat: @" order by date limit 400"] arguments: args];
	va_end(args);

	return retval;
}

- (NSArray *) itemsInTag:(NSString *) tag{
	BOOL showReadItems = [[[[UIApplication sharedApplication] delegate] settings] showReadItems];
	if(!tag) {
		return [self enumeratorWithConstructor:@selector(tagItemFromResultSet:) forQuery:[NSString stringWithFormat:@"select feed_name, count(google_id) as num_items from items %@ GROUP BY feed_name ORDER BY feed_name", showReadItems? @"" : @"where is_read = 0"]];
	} else {
		NSString * condition = nil;
		if(!showReadItems) {
			condition = @"is_read = 0";
		}
		id result;
		if([tag isEqualToString:all_items_tag]) {
			result = [self itemsMatchingCondition: condition];
		} else {
			NSString * additionalCondition = @"feed_name = ?";
			condition = condition? [condition stringByAppendingFormat: @" and %@", additionalCondition] : additionalCondition;
			result = [self itemsMatchingCondition: condition, tag ];
		}
		dbg(@"condition = %@", condition);
		return result;
	}
}

#pragma mark convenience query methods
- (NSEnumerator *) allItems		{ return [self itemsMatchingCondition: nil]; }
- (NSEnumerator *) unreadItems	{ return [self itemsMatchingCondition: @"is_read = 0"]; }
- (NSEnumerator *) readItems	{ return [self itemsMatchingCondition: @"is_read = 1"]; }
- (NSEnumerator *) starredItems { return [self itemsMatchingCondition: @"is_starred = 1"]; }
- (NSEnumerator *) locallyModifiedItems { return [self itemsMatchingCondition: @"dirty = 1"]; }

- (id) itemWithID: (NSString *) google_id {
	return [self itemFromResultSet: [db executeQuery: @"select * from items where google_id = ?", google_id]];
}

- (void) setAllItemsReadState: (BOOL) readState forTag:(NSString *) tag {
	dbg(@"DB: marking all items as %s", read ? "read" : "unread");
	if(tag == nil || [tag isEqualToString: all_items_tag]) {
		[db executeUpdate: @"update items set is_read=?", [NSNumber numberWithBool: readState]];
	} else {
		[db executeUpdate: @"update items set is_read=? where feed_name = ?", [NSNumber numberWithBool: readState], tag];
	}
	if_error [NSException raise:@"UpdateFailed" format:@"updating marking all items as %s failed", readState ? "read":"unread"];
}
@end




@implementation FeedItemEnumerator : NSEnumerator
- (id) initWithResultSet: result_set fromDB:(ItemDB *) the_db withConstructor:(SEL)_constructor {
	self = [super init];
	rs = [result_set retain];
	db = [the_db retain];
	constructor = _constructor;
	return self;
}
- (id) nextObject {
	if(![rs next]){
		return nil;
	}
	return [self construct: rs];
}

- (id) construct:(id) rs {
	return [db performSelector:constructor withObject: rs];
}

- (void) dealloc {
	[rs close];
	[rs release];
	[db release];
	[super dealloc];
}

- (NSArray *) allObjects {
	NSMutableArray *array = [NSMutableArray array];
	while([rs next]) {
		[array addObject: [self construct: rs]];
	}
	return array;
}
@end

@interface itemProxy : NSObject {
	NSString * obj_id;
	ItemDB * db;
	SEL constructor;
	id * _item;
}
@end

@implementation itemProxy : NSObject
- (id) initWithID: (NSString *)_id fromSource:(ItemDB *)_db usingConstructor:(SEL)_sel {
	self = [super init];
	obj_id = [_id retain];
	db = [_db retain];
	constructor = _sel;
	return self;
}

- (void) deflate {
	[_item release];
	_item = nil;
}

- (id) fullItem {
	if(!_item) {
		_item = [db performSelector:constructor withObject:obj_id];
	}
	return _item;
}

- (void) forwardInvocation:(NSInvocation *)invocation {
	[invocation invokeWithTarget: [self fullItem]];
}

- (void) dealloc {
	[db release];
	[obj_id release];
	[_item release];
	[super dealloc];
}
@end
