import globalPluginHandler
import config
import gui
import scriptHandler
import ui
import winKernel
import wx
from logHandler import log
import addonHandler
addonHandler.initTranslation()


class WakeTimer(wx.Timer):
	def Notify(self):
		log.info("reseting")
		winKernel.SetThreadExecutionState(winKernel.ES_SYSTEM_REQUIRED)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super().__init__()
		self.timer = None
		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		self.menuItem = self.toolsMenu.AppendCheckItem(wx.ID_ANY, _("S&leep Blocker"), _("Toggles Sleep Blocker."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, lambda event: self.toggle(), self.menuItem)

	@scriptHandler.script(
		description=_("Prevent the system from going into sleep mode. Togglable"),
		gesture="kb:NVDA+control+shift+c")
	def script_toggleDisableSleep(self, gesture):
		self.toggle()

	def toggle(self):
		if not self.timer:
			self.timer = WakeTimer()
			self.timer.Start(5000)
			log.info("Enabled")
			self.menuItem.Check()
			ui.message(_("Sleep Blocker Enabled."))
		elif self.timer:
			self.timer.Stop()
			self.timer = None
			log.info("Disabled")
			self.menuItem.Check(False)
			ui.message(_("Sleep Blocker disabled."))

	def terminate(self):
		super().terminate()
		if self.timer:
			if self.timer.IsRunning():
				self.timer.stop()
			self.timer = None
		self.toolsMenu.Delete(self.menuItem)
		self.menuItem = None


confspec = {
	"blockDisplaySleep": "boolean(default=false)"
}
config.conf.spec["sleepBlocker"] = confspec


class SleepBlockerSettings(gui.settingsDialogs.SettingsPanel):
	title = _("Sleep Blocker")

	def makeSettings(self, panelSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=panelSizer)
		self.BlockDisplayCB = sHelper.addItem(
			wx.CheckBox(self, label=_("Also block the &display from sleeping"))
		)
		self.BlockDisplayCB.SetValue(config.conf["sleepBlocker"]["blockDisplaySleep"])

	def onSave(self):
		config.conf["sleepBlocker"]["blockDisplaySleep"] = self.BlockDisplayCB.IsChecked()
