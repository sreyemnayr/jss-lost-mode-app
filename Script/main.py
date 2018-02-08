import ui
import dialogs
import console
import shelve
import sys

from jssapi import JSSApi

device_list = []
which_device = None

def enable(sender):
    '@type sender: ui.Button'
    global device_list, which_device, loading, v, api
    
    loading.hidden = False
    turn(loading)
    label = sender.superview['name']
    message = sender.superview['message'].text
    tv = sender.superview['textview']
    text = ''
    if which_device is None:
        devices = api.get('mobiledevices/match/'+str(label.text))
    else:
        devices = []
        devices.append(device_list[which_device])
    for device in devices:
        text = str(device['id'])
        xml = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><mobile_device_command><command>EnableLostMode</command><lost_mode_message>{msg}</lost_mode_message><lost_mode_with_sound>true</lost_mode_with_sound><mobile_devices><mobile_device><id>{id}</id></mobile_device></mobile_devices></mobile_device_command>".format(id=text,msg=message)
        command = "mobiledevicecommands/command/EnableLostMode"
        api.post(method=command,body=xml)
        tv.text = xml+"\n"+command+"\n"+api.r.text
        loading.hidden = True

def disable(sender):
    '@type sender: ui.Button'
    global device_list, which_device, loading, v
    loading.hidden=False
    
    label = sender.superview['name']
    #console.alert(label.text)
    tv = sender.superview['textview']
    text = ''
    if which_device is None:
        devices = api.get('mobiledevices/match/'+str(label.text))
    else:
        devices = []
        devices.append(device_list[which_device])
    for device in devices:
        text = str(device['id'])
        xml = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><mobile_device_command><command>DisableLostMode</command><mobile_devices><mobile_device><id>{id}</id></mobile_device></mobile_devices></mobile_device_command>".format(id=text)
        command = "mobiledevicecommands/command/DisableLostMode"
        api.post(method=command,body=xml)
        tv.text = xml+"\n"+command+"\n"+api.r.text
    loading.hidden = True

def get_devices():
    global device_list, v, loading, d, api
    #d = shelve.open('settings')
    #v['textview'].text += "\n get_devices start "+str(d)
    #d.close()
    loading.hidden = False
    device_list[:]
    devices = api.get('mobiledevices')
    for device in devices:
        device_list.append({'id':device['id'],'name':device['name']})
    device_list = sorted(device_list, key=lambda k: k['name'])
    loading.hidden = True
    #d = shelve.open('settings')
    #v['textview'].text += "\n get_devices end "+str(d)
    #d.close()

def slider_change(sender):
    '@type sender: ui.Slider'
    global which_device
    val = sender.value
    tf = sender.superview['name']
    num_devices = len(device_list)
    which_device = int( ( num_devices - 1 ) * val)
    tf.text = str(device_list[which_device]['id']) + ' ' + str(device_list[which_device]['name'])

def slider_up(sender):
    '@type sender: ui.Button'
    global d, device_list
    #d = shelve.open('settings',writeback=True)
    #v['textview'].text += "\n slider_up start "+str(d)
    #fields = []
    num_devices = len(device_list)
    step = 1.0 / float(num_devices)
    slider = sender.superview['slider']
    val = slider.value + step
    slider.value = val
    slider_change(slider)

def slider_down(sender):
    '@type sender: ui.Button'
    num_devices = len(device_list)
    step = 1.0 / float(num_devices)
    slider = sender.superview['slider']
    val = slider.value - step
    slider.value = val
    slider_change(slider)

def use_textfield(sender):
    '@type sender: ui.TextField'
    global which_device
    which_device = None

def turn(sender):
    def a():
        sender.transform = ui.Transform.rotation(360)
    ui.animate(a,duration=.2,completion=turn)

def show_settings(sender):
    '@type sender: ui.Button'
    global api, d
    #d = shelve.open('settings',writeback=True)
    #v['textview'].text += "\n show_settings start "+str(d)
    fields = []
    fields.append({'type':'text','key':'url','value':str(d['url']),'title':'JSS URL'})
    fields.append({'type':'text','key':'usr','value':str(d['usr']),'title':'API Username'})
    fields.append({'type':'text','key':'pwd','value':str(d['pwd']),'title':'API Password'})
    fields.append({'type':'text','key':'msg','value':str(d['msg']),'title':'Default Message'})
    settings = dialogs.form_dialog(title='Settings',fields=fields)
    d['url'] = settings['url']
    d['usr'] = settings['usr']
    d['pwd'] = settings['pwd']
    d['msg'] = settings['msg']
    sender.superview['message'].text = d['msg']
    d.sync()
    #d.close()
    #d = shelve.open('settings')
    #v['textview'].text += "\n show_settings pre-API"+str(d)
    #d.close()
    api = JSSApi(url=settings['url'],user=settings['usr'],pwd=settings['pwd'])
    checkuser = api.get(method='accounts/username/'+settings['usr'])
    v['textview'].text = api.r.text
    
    get_devices()
v = ui.load_view('findipad')
v.content_mode = ui.CONTENT_CENTER
v.present('fullscreen',hide_title_bar=True)

#w,h = ui.get_screen_size()

loading = v['loading']
turn(loading)



try:
    d = shelve.open('jsssettings','c', writeback=True)
    #v['textview'].text += "\n main:try "+str(d)
    url = d['url']
    usr = d['usr']
    pwd = d['pwd']
    msg = d['msg']
    v['message'].text = msg
    d.sync()
    api = JSSApi(url=url,user=usr,pwd=pwd)
    get_devices()
except:
    #d = shelve.open('settings',writeback=True)
    d['url'] = 'https://your.jamfserver.local:8443'
    d['usr'] = 'apiuser'
    d['pwd'] = 'apipw'
    d['msg'] = 'Please return to technology coordinator'
    d.sync()
    #v['textview'].text += "\n main:except "+str(d)
    #d.close()
    #console.alert(str(sys.exc_info()[0]))
    show_settings(v['settingsBtn'])
    #d = shelve.open('settings')
    #v['textview'].text += "\n main:except post show_settings "+str(d)
    #d.close()



v["name"].action=use_textfield

#d = shelve.open('settings')
#v['textview'].text += "\n main post-except "+str(d)
#d.close()

