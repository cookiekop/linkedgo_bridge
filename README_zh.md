
# 零狗智能HomeAssistant插件

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


安装完成后会提示重启。进入 设置 > 系统 > 点击右上角重启按钮，重启完成后进入**Linkedgo Bridge**插件配置




## 配置插件

### 零狗APP
1. 下载零狗APP，并注册用户账号
2. 创建住宅
3. 使用零狗APP完成设备添加，并分配楼层、房间信息



### Linkedgo Bridge 配置

1. 设置 > 设备与服务 

2. 点击右下角 添加集成 

3.  搜索 **Linkedgo Bridge** 

4. 点击**Linkedgo Bridge**进行登录 > 使用零狗APP账号登录

5. 登录成功后，弹出会话框**选择住宅与设备**，您可以选择需要添加的住宅，将该住宅内的所有设备将导入 Home Assistant 



[使用说明](./specification.md)
