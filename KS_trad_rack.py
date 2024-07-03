import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return TradRackPanel(*args)


class TradRackPanel(ScreenPanel):
    lanes = ['0', '1']
    lane = lanes[0]

    def __init__(self, screen, title):
        super().__init__(screen, title)
        self.settings = {}
        self.menu = ['tracd_rack_menu']
        self.buttons = {
            'home': self._gtk.Button("home", _("Home"), "color1"),
            'resume': self._gtk.Button("resume", _("Resume"), "color1"),
            'goto_lane': self._gtk.Button("move", _("Goto Lane"), "color2"),
            'load_lane': self._gtk.Button("arrow-down", _("Load Lane"), "color2"),
            'set_active_lane': self._gtk.Button("arrow-down", _("Set Act. Lane"), "color2"),
            'load_toolhead': self._gtk.Button("arrow-down", _("Load ToolHead"), "color3"),
            'unload': self._gtk.Button("arrow-up", _("Unload"), "color3"),
            'reset_active_lane': self._gtk.Button("arrow-up", _("Reset Act. Lane"), "color3"),

            'servo_up': self._gtk.Button("z-farther", _("Servo Up"), "color4"),
            'servo_down': self._gtk.Button("z-closer", _("Servo Down"), "color4"),
        }

        self.buttons['home'].connect("clicked", self.tr_cmd, "TR_HOME")
        self.buttons['resume'].connect("clicked", self.tr_cmd, "TR_RESUME")
        self.buttons['servo_up'].connect("clicked", self.tr_cmd, "TR_SERVO_UP")
        self.buttons['servo_down'].connect("clicked", self.tr_cmd, "TR_SERVO_DOWN")
        self.buttons['goto_lane'].connect("clicked", self.goto_lane_act)
        self.buttons['load_lane'].connect("clicked", self.load_lane_act)
        self.buttons['set_active_lane'].connect("clicked", self.set_active_lane_act)
        self.buttons['load_toolhead'].connect("clicked", self.load_toolhead_act)
        self.buttons['reset_active_lane'].connect("clicked", self.tr_cmd, "TR_RESET_ACTIVE_LANE")
        self.buttons['unload'].connect("clicked", self.unload_act)

        if 'trad_rack' in self._printer.get_config_section_list():
            trad_rack_cfg = self._printer.get_config_section("trad_rack")
            if 'lane_count' in trad_rack_cfg:
                self.lanes = []
                for i in range(int(float(trad_rack_cfg["lane_count"]))):
                    self.lanes.append(str(i))
#                self.lanes = map(str, range(int(float(trad_rack_cfg["lane_count"]))))
                self.lane = self.lanes[0]

        selectgrid = Gtk.Grid()
        lane_row = 0
        lane_col = 0
        for j, i in enumerate(self.lanes):
            self.labels[i] = self._gtk.Button(label=i)
            self.labels[i].set_direction(Gtk.TextDirection.LTR)
            self.labels[i].connect("clicked", self.change_lane, i)
            ctx = self.labels[i].get_style_context()
            if (self._screen.lang_ltr and j == 0) or (not self._screen.lang_ltr and j == len(self.lanes) - 1):
                ctx.add_class("distbutton_top")
            elif (not self._screen.lang_ltr and j == 0) or (self._screen.lang_ltr and j == len(self.lanes) - 1):
                ctx.add_class("distbutton_bottom")
            else:
                ctx.add_class("distbutton")
            if i == self.lane:
                ctx.add_class("distbutton_active")

            lane_col = j % 6
            if j != 0 and lane_col == 0:
                lane_row = lane_row + 1
            selectgrid.attach(self.labels[i], lane_col, lane_row, 1, 1)

        for p in ('curr_lane', 'active_lane', 'retry_lane', 'next_lane'):
            self.labels[p] = Gtk.Label()
            ctx = self.labels[p].get_style_context()
            ctx.add_class(f"{p}_text")

        self.labels['select_lane'] = Gtk.Label(_("Select Lanes"))
        self.labels['servo'] = Gtk.Label(_("Servo"))
        self.labels['toolhead'] = Gtk.Label(_("Tool Head"))

        topgrid = self._gtk.HomogeneousGrid()
        topgrid.set_direction(Gtk.TextDirection.LTR)
        topgrid.attach(self.labels['curr_lane'], 0, 0, 1, 1)
        topgrid.attach(self.labels['active_lane'], 1, 0, 1, 1)
        topgrid.attach(self.labels['retry_lane'], 2, 0, 1, 1)
        topgrid.attach(self.labels['next_lane'], 3, 0, 1, 1)

#        grid = self._gtk.HomogeneousGrid()
#        if self._screen.vertical_mode:
#        grid.attach(self.buttons['home'], 0, 0, 1, 1)
#        grid.attach(self.buttons['resume'], 1, 0, 1, 1)

        lanegrid = self._gtk.HomogeneousGrid()
        lanegrid.attach(self.labels['select_lane'], 0, 0, 1, 1)
        lanegrid.attach(self.buttons['home'], 1, 0, 1, 1)
        lanegrid.attach(self.buttons['resume'], 2, 0, 1, 1)
        lanegrid.attach(selectgrid, 0, 1, 3, 1)
        lanegrid.attach(self.buttons['goto_lane'], 0, 2, 1, 1)
        lanegrid.attach(self.buttons['load_lane'], 1, 2, 1, 1)
        lanegrid.attach(self.buttons['set_active_lane'], 2, 2, 1, 1)
        lanegrid.attach(self.buttons['load_toolhead'], 0, 3, 1, 1)
        lanegrid.attach(self.buttons['unload'], 1, 3, 1, 1)
        lanegrid.attach(self.buttons['reset_active_lane'], 2, 3, 1, 1)
        
#        toolheadgrid = self._gtk.HomogeneousGrid()
#        toolheadgrid.attach(self.labels['toolhead'], 0, 0, 3, 1)
#        toolheadgrid.attach(self.buttons['load_toolhead'], 0, 1, 1, 1)
#        toolheadgrid.attach(self.buttons['unload'], 1, 1, 1, 1)
#        toolheadgrid.attach(self.buttons['reset_active_lane'], 2, 1, 1, 1)
        
        servogrid = self._gtk.HomogeneousGrid()
        servogrid.attach(self.labels['servo'], 0, 0, 1, 1)
        servogrid.attach(self.buttons['servo_up'], 1, 0, 1, 1)
        servogrid.attach(self.buttons['servo_down'], 2, 0, 1, 1)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.pack_start(topgrid, False, True, 0)
#        box.add(grid)
        box.add(lanegrid)
#        box.add(toolheadgrid)
        box.add(servogrid)

        scroll = self._gtk.ScrolledWindow()
        scroll.add(box)
        self.content.add(scroll)

    def process_busy(self, busy):
        buttons = ("resume")
        for button in self.buttons:
            if button not in self.buttons:
                self.buttons[button].set_sensitive(not busy)

    def all_lane_remove_class(self, class_name):
        for lane in self.lanes:
            ctx = self.labels[lane].get_style_context()
            ctx.remove_class(class_name)

    def process_update(self, action, data):
        if action == "notify_busy":
            self.process_busy(data)
            return
        if action != "notify_status_update":
            return
        if 'trad_rack' in data:
                trad_rack_data = data['trad_rack']
                if 'curr_lane' in trad_rack_data:
                    curr_lane = trad_rack_data['curr_lane']
                    self.labels['curr_lane'].set_text(f"C {curr_lane}")
                    self.all_lane_remove_class('curr_lane')
                    if f"{curr_lane}" in self.labels:
                        logging.info(f"### Style Lane {curr_lane}")
                        ctx = self.labels["0"].get_style_context()
                        ctx.add_class("curr_lane")

                if 'active_lane' in trad_rack_data:
                    active_lane = trad_rack_data['active_lane']
                    self.labels['active_lane'].set_text(f"A {active_lane}")
                    self.all_lane_remove_class('active_lane')
                    if active_lane in self.labels:
                        ctx = self.labels[active_lane].get_style_context()
                        ctx.add_class(f"active_lane")

                if 'retry_lane' in trad_rack_data:
                    retry_lane = trad_rack_data['retry_lane']
                    self.labels['retry_lane'].set_text(f"R {retry_lane}")
                    self.all_lane_remove_class('retry_lane')
                    if retry_lane in self.labels:
                        ctx = self.labels[retry_lane].get_style_context()
                        ctx.add_class(f"retry_lane")

                if 'next_lane' in trad_rack_data:
                    next_lane = trad_rack_data['next_lane']
                    self.labels['next_lane'].set_text(f"N {next_lane}")
                    self.all_lane_remove_class('next_lane')
                    if next_lane in self.labels:
                        ctx = self.labels[next_lane].get_style_context()
                        ctx.add_class(f"next_lane")

    def change_lane(self, widget, lane):
        logging.info(f"### Lane {lane}")
        self.labels[f"{self.lane}"].get_style_context().remove_class("distbutton_active")
        self.labels[f"{lane}"].get_style_context().add_class("distbutton_active")
        self.lane = lane

    def tr_cmd(self, widget, cmd):
        self._screen._ws.klippy.gcode_script(cmd)

    def goto_lane_act(self, widget):
        lane = f"{self.lane}"
        self._screen._ws.klippy.gcode_script(f"TR_GO_TO_LANE LANE={lane}")

    def load_lane_act(self, widget):
        lane = f"{self.lane}"
        self._screen._ws.klippy.gcode_script(f"TR_LOAD_LANE LANE={lane}")

    def set_active_lane_act(self, widget):
        lane = f"{self.lane}"
        self._screen._ws.klippy.gcode_script(f"TR_SET_ACTIVE_LANE LANE={lane}")
        
    def load_toolhead_act(self, widget):
#        for d in (self._printer.get_tools()):
#            if self._printer.get_dev_stat(x, "temperature") < 190:
#                self._screen.show_popup_message(_("extruder temp too low!"))
#                return

        lane = f"{self.lane}"
        self._screen._ws.klippy.gcode_script(f"TR_LOAD_TOOLHEAD LANE={lane}")

    def unload_act(self, widget):
#        for d in (self._printer.get_tools()):
#            if self._printer.get_dev_stat(x, "temperature") < 190:
#                self._screen.show_popup_message(_("extruder temp too low!"))
#                return

        self._screen._ws.klippy.gcode_script("TR_UNLOAD_TOOLHEAD")
