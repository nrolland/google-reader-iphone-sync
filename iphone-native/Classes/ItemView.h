#import <UIKit/UIKit.h>
#import "ItemDB.h"

@interface ItemView : UIWebView {
	IBOutlet id appDelegate;
	IBOutlet id titleDisplay;

	IBOutlet id buttonPrev;
	IBOutlet id buttonNext;
	IBOutlet id buttonStar;
	IBOutlet id buttonShare;
	IBOutlet id buttonRead;
	
	IBOutlet ItemDB * db;
	id nextCursor;
	id prevCursor;
	NSString * currentHTML;
	NSMutableArray * allItems;
	int currentItemIndex;
	FeedItem * currentItem;
}
- (void) loadHTMLString: (NSString *) newHTML;
- (void) loadItem: (FeedItem *) item;
- (IBAction) loadUnread;
- (void) loadItemAtIndex:(int) index fromSet: (id) items;
- (void) setButtonStates;
- (BOOL) canGoNext;
- (BOOL) canGoPrev;
- (void) loadItemAtIndex:(int) index;
- (NSString *) currentItemID;

- (IBAction) toggleStarForCurrentItem:(id) sender;
- (IBAction) toggleReadForCurrentItem:(id) sender;
- (IBAction) toggleSharedForCurrentItem:(id) sender;
- (IBAction) emailCurrentItem:(id) sender;
@end
