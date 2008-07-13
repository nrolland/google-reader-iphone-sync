import objc
from _uicaboodle import *
from objc import YES, NO, NULL

from src.config import load_config
import src.app_globals as app_globals

objc.loadBundle("Celestial", globals(), "/System/Library/Frameworks/Celestial.framework")
objc.loadBundle("UIKit", globals(), "/System/Library/Frameworks/UIKit.framework")


class FeedList(NSObject):
	def init(self):
		self.subscriptions = app_globals.OPTIONS['tag_list']
		return self

	# tableview datasource methods
	@objc.signature("@@:@i@@")
	def table_cellForRow_column_reusing_(self, table, row, col, reusing):
		if reusing is not None:
			cell = reusing
		else:
			cell = UIImageAndTextTableCell.alloc().init()
		cell.setTitle_(self.subscriptions[row])
		return cell
		
	@objc.signature("i@:@")
	def numberOfRowsInTable_(self, table):
		return len(self.subscriptions)
	
	

class PYApplication(UIApplication):
	@objc.signature("v@:@")
	def applicationDidFinishLaunching_(self, unused):
		outer = UIHardware.fullScreenApplicationContentRect()
		self.window = UIWindow.alloc().initWithFrame_(outer)

		self.window.orderFront_(self)
		self.window.makeKey_(self)
		self.window._setHidden_(NO)

		inner = self.window.bounds()
		navsize = UINavigationBar.defaultSize()
		navrect = ((0, 0), (inner[1][0], navsize[1]))

		self.view = UIView.alloc().initWithFrame_(self.window.bounds())
		self.window.setContentView_(self.view)

		self.navbar = UINavigationBar.alloc().initWithFrame_(navrect);
		self.view.addSubview_(self.navbar)

		self.navbar.setBarStyle_(1)

		navitem = UINavigationItem.alloc().initWithTitle_("Feed List")
		self.navbar.pushNavigationItem_(navitem)
		
		# add a tableView
		load_config()
		lower = ((0, navsize[1]), (inner[1][0], inner[1][1] - navsize[1]));
		self.table = UITable.alloc().initWithFrame_(lower)
		self.view.addSubview_(self.table)

		col = UITableColumn.alloc().initWithTitle_identifier_width_("Name", "name", 320)

		self.table.setSeparatorStyle_(1)
		self.table.addTableColumn_(col)
		self.table.setReusesTableCells_(YES)

		self.feed_list = FeedList.alloc().init()
		self.table.setDataSource_(self.feed_list)
		self.table.reloadData()

	
UIApplicationMain(["GRiS"], PYApplication)
