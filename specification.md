
# Linkedgo Bridge 使用说明

[English](./README.md) | [简体中文](.README_zh.md)

<p align="left">
  <img src="http://smartspeaker.linked-go.com/iotapplet-image/ha_logo.png" alt="零狗智能" title="零狗智能" la="la">
</p>

Linekdgo Bridge 是由零狗官方提供支持的 Home Assistant 的集成组件，用于在 Home Assistant 平台控制您的零狗智能设备，目前已经支持温控类产品（ST830 蓝牙青春版, ST1800-HN 单地暖, ST2000 极光板）。

## 安装

> Home Assistant 版本要求：
>
> - Core >= 2024.4.4
> - Operating System >= 13.0


### 方法1: [HACS](https://hacs.xyz/)社区商店安装

HACS > 在搜索框中输入 **Linkedgo Bridge** > 点击搜索结果 **Linkedgo Bridge** ，进入集成详情页  > 点击右下方 **下载** 按钮 安装

<p align="left">
  <img src="http://smartspeaker.linked-go.com/iotapplet-image/hacs_step1.png">
</p>

安装完成后会提示重启。进入 设置 > 系统 > 点击右上角重启按钮，重启完成后进入**Linkedgo Bridge**插件配置




## 配置插件

### 零狗APP
1. 下载零狗APP，并注册用户账号
2. 创建住宅
3. 使用零狗APP完成设备添加，并分配楼层、房间信息



### Linkedgo Bridge 配置

1. 设置 > 设备与服务 

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/homekit_step1.png">
   </p>

2. 点击右下角 添加集成 

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/homekit_step2.png">
   </p>

3.  搜索 **Linkedgo Bridge** 

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/hacs_step4.png">
   </p>

4. 点击**Linkedgo Bridge**进行登录 > 使用零狗APP账号登录

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/hacs_step5.png">
   </p>

5. 登录成功后，弹出会话框**选择住宅与设备**，您可以选择需要添加的住宅，将该住宅内的所有设备将导入 Home Assistant 



## 设备控制

### 面板主页

<p align="left">
  <img src="http://smartspeaker.linked-go.com/iotapplet-image/ha_control_main.PNG" alt="面板主页" title="面板主页" la="la">
</p>

### 更多设置

<p align="left">
  <img src="http://smartspeaker.linked-go.com/iotapplet-image/ha_control_more.PNG" alt="更多设置" title="更多设置" la="la">
</p>

# HomeKit配置
1. 依次点击【设置】，【设备与服务】

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/homekit_step1.png">
   </p>

2. 点击右下角，【添加集成】

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/homekit_step2.png">
   </p>

3. 搜【apple】，出来的结果，点击【Apple】

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/homekit_step3.png">
   </p>

4. 点击搜索结果中的【HomeKit Bridge】

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/homekit_step4.png">
   </p>

5. 选择需要包含的域，然后点击【提交】

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/homekit_step5.png">
   </p>

6. 提示“与HomeKit”配对，点击【提交】

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/homekit_step6.png">
   </p>

7. 点击【完成】

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/homekit_step7.png">
   </p>

8. 点击左侧【通知】，会有二维码，然后打开苹果手机的家庭 app，扫码添加



# 产品功能

### ST830 青春版温控器(蓝牙版)

| 功能         | 注释                                                   |
| ------------ | ------------------------------------------------------ |
| 开关机       | 开机（切换任意模式即开机）/关机                        |
| 模式         | 制冷/制热/通风/除湿                                    |
| 风速         | 自动/高/中/低（交流）；自动/1档/2档/3档/4档/5档 (直流) |
| 温度设置     | 设置范围 5℃ ~ 35℃，精度0.5℃                            |
| 除湿湿度设置 | 设置范围 40% ~ 75%，精度1%                             |
| 睡眠模式开关 |                                                        |
| 室内温度     | 仅显示                                                 |
| 室内湿度     | 仅显示                                                 |
| 恒温停机     | 恒温停机时显示 “空闲”                                  |



### ST2000 极光温控器

| 功能         | 注释                                                   |
| ------------ | ------------------------------------------------------ |
| 开关机       | 开机（切换任意模式即开机）/关机                        |
| 模式         | 制冷/制热/通风/除湿                                    |
| 风速         | 自动/高/中/低（交流）；自动/1档/2档/3档/4档/5档 (直流) |
| 温度设置     | 设置范围 5℃ ~ 35℃，精度0.5℃                            |
| 除湿湿度设置 | 设置范围 40% ~ 75%，精度1%                             |
| 睡眠模式开关 |                                                        |
| 室内温度     | 仅显示                                                 |
| 室内湿度     | 仅显示                                                 |
| 恒温停机     | 恒温停机时显示 “空闲”                                  |



### ST1800-HN 星光地暖温控器

| 功能     | 注释                            |
| -------- | ------------------------------- |
| 开关机   | 开机（切换制热模式即开机）/关机 |
| 模式     | 制热                            |
| 温度设置 | 设置范围 5℃ ~ 50℃，精度0.5℃     |
| 室内温度 | 仅显示                          |
| 室内湿度 | 仅显示                          |
| 恒温停机 | 恒温停机时显示 “空闲”           |





# 常见问题

### 新添加的设备同步到HomeAssistant

1. 设置 > 选择上方 集成 > 点击**Linkedgo Bridge**集成

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/ha_QA_reconfigration_step1.png">
   </p>

2. **Linkedgo Bridge**集成详情页 > 点击 **...**  > 点击 重新加载

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/ha_QA_reconfigration_step2.png">
   </p>

### 查找设备MAC

1. 面板主页 > 更多设置 > 设置图标

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/ha_QA_findmac_step1.png"  width="50%">
   </p>

2. 实体标识符的下划线组合为设备MAC

   <p align="left">
     <img src="http://smartspeaker.linked-go.com/iotapplet-image/ha_QA_findmac_step2.png"  width="50%">
   </p>





