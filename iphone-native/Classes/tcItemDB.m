#import <Foundation/Foundation.h>
#import "FMDatabase.h"
#import "FMDatabaseAdditions.h"
#import "tcHelpers.h"
#import "tcItemDB.h"
#import "tcItem.h"

@interface tcItemEnumerator : NSEnumerator {
	FMResultSet* rs;
	tcItemDB * db;
}
- (id) initWithResultSet: result_set fromDB:(tcItemDB *) the_db;
@end


@implementation tcItemDB

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
	[db close];
	[db release];
	[super dealloc];
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
	 return [[[tcItem alloc]
			 initWithId:	[rs stringForColumn:@"google_id"]
			 date:			[rs stringForColumn:@"date"]
			 url:			[rs stringForColumn:@"url"]
			 title:			[rs stringForColumn:@"title"]
			 content:		[rs stringForColumn:@"content"]
			 is_read:		[rs boolForColumn:@"is_read"]
			 is_starred:	[rs boolForColumn:@"is_starred"]
			 db: self]
		autorelease];
}

- (NSEnumerator *) enumeratorForQuery: (NSString *) sql, ... {
	va_list args;
	va_start(args, sql);
	
	dbg(@"** SQL: enumeratorForQuery: %@", sql);
	FMResultSet *rs = [db executeQuery:sql arguments:args];
	
	va_end(args);
	if_error return nil;
	
	return [[[tcItemEnumerator alloc] initWithResultSet:rs fromDB: self] autorelease];
}

- (NSEnumerator *) itemsMatchingCondition:(NSString *) condition {
	NSString * query = @"select * from items";
	if(condition != nil){
		query = [query stringByAppendingFormat: @" where %@ order by date", condition];
	}
	return [self enumeratorForQuery: query];
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

@end

@implementation tcItemEnumerator : NSEnumerator
- (id) initWithResultSet: result_set fromDB:(tcItemDB *) the_db {
	self = [super init];
	rs = result_set;
	db = [the_db retain];
	[rs retain];
	return self;
}
- (id) nextObject {
	if(![rs next]){
		return nil;
	}
	return [db itemFromResultSet: rs];
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
		[array addObject: [db itemFromResultSet: rs]];
	}
	return array;
}
@end

@interface itemProxy : NSObject {
	NSString * google_id;
	tcItemDB * db;
}
@end
@implementation itemProxy : NSObject
- (id) initWithID: (NSString *)ngoogle_id fromSource:(tcItemDB *)ndb {
	self = [super init];
	google_id = [ngoogle_id retain];
	db = [ndb retain];
	return self;
}

- (void) forwardInvocation:(NSInvocation *)invocation {
	[invocation invokeWithTarget: [db itemWithID: google_id]];
}

- (void) dealloc {
	[db release];
	[google_id release];
	[super dealloc];
}
@end