#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

@interface ItemListController : UIViewController {
	IBOutlet id listView;
	IBOutlet id delegate;

	UIAlertView * markAsReadAlert;
	BOOL alertWasForMarkingAsRead;
	id navigationItem;
}
- (IBAction) refresh: (id) sender;
- (IBAction) markAllItemsAsRead:(id) sender;
- (IBAction) markAllItemsAsUnread:(id) sender;
@end
