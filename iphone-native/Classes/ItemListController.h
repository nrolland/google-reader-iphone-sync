#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

@interface ItemListController : UIViewController {
	IBOutlet id listView;
	IBOutlet id delegate;
	IBOutlet id optionsView;
	BOOL optionsAreVisible;
	IBOutlet id showHideOptionsButton;

	UIAlertView * markAsReadAlert;
	BOOL alertWasForMarkingAsRead;
	id navigationItem;
}
- (IBAction) toggleOptions:(id)sender;
- (IBAction) refresh: (id) sender;
- (IBAction) markAllItemsAsRead:(id) sender;
- (IBAction) markAllItemsAsUnread:(id) sender;
@end
