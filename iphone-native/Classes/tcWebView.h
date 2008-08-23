#import <UIKit/UIKit.h>
#import "tcItemDB.h"

@interface tcWebView : UIWebView {
	IBOutlet id appDelegate;
	IBOutlet id titleDisplay;

	IBOutlet id buttonPrev;
	IBOutlet id buttonNext;
	IBOutlet id buttonStar;
	IBOutlet id buttonRead;
	
	IBOutlet tcItemDB * db;
	id nextCursor;
	id prevCursor;
	NSString * currentHTML;
	NSMutableArray * allItems;
	int currentItemIndex;
	tcItem * currentItem;
}
- (void) loadHTMLString: (NSString *) newHTML;
- (void) loadItem: (tcItem *) item;
- (IBAction) loadUnread;
- (void) loadItemAtIndex:(int) index fromSet: (id) items;
- (void) setButtonStates;
- (BOOL) canGoNext;
- (BOOL) canGoPrev;
- (void) loadItemAtIndex:(int) index;
- (NSString *) currentItemID;

- (IBAction) toggleStarForCurrentItem:(id) sender;
- (IBAction) toggleReadForCurrentItem:(id) sender;
- (IBAction) emailCurrentItem:(id) sender;
@end
