#import "Foundation/Foundation.h"
#import "tcItemDB.h"

@interface tcItem : NSObject {
	NSString* google_id;
	NSString* date;
	NSString* url;
	NSString* title;
	NSString* content;
	id source_db;
	BOOL is_read;
	BOOL is_starred;
	BOOL is_dirty;
	BOOL sticky_read_state;
}

- (id) initWithId: (NSString *) google_id
	date: (NSString *) date
	url: (NSString *) url
	title: (NSString *) title
	content: (NSString *) content
	is_read: (BOOL) is_read
	is_starred:	(BOOL) is_starred
	db:(id) source_db;

- (void) save;

@property(readonly) NSString* google_id;
@property(readonly) NSString* date;
@property(readonly) NSString* url;
@property(readonly) NSString* title;
@property(readonly) NSString* content;
@property(readonly) BOOL is_read;
@property(readonly) BOOL is_starred;
@property(readonly) BOOL is_dirty;

- (NSString *) html;
- (void) userDidScrollPast;
- (BOOL) userHasMarkedAsRead;
- (BOOL) toggleReadState;
- (BOOL) toggleStarredState;	
@end
