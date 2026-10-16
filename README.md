# FirstKotlinApp

实验二：Android 网络访问与 Git 个人仓库。

## 实验目标

- 在 Jetpack Compose 页面中发起真实的 HTTPS 和 HTTP 请求，查看状态码及部分响应正文。
- 区分 `INTERNET` 权限与 HTTP 明文通信配置，并比较禁止、允许明文通信时的结果。
- 将项目源码与配置提交并推送到个人 Git 仓库。

## 运行方式

1. 使用 Android Studio 打开本项目根目录，等待 Gradle 同步完成。
2. 连接可联网的 Android 设备或启动模拟器（项目最低支持 API 24），选择 `app` 运行配置并点击 **Run**。
3. 在页面中点击 **HTTPS 请求**，查看请求地址、HTTP 状态码和响应正文中的 `room` 参数。
4. 点击 **HTTP 请求**，对比相同接口在明文通信配置下的结果。修改 `network_security_config.xml` 后，需要重新构建并安装应用，配置才会作用于设备上的新版本。

也可以在项目根目录执行 `gradlew.bat :app:assembleDebug` 构建调试 APK；Windows 环境下请使用 Android Studio 附带的 JDK 或已正确配置的 JDK。

## 接口地址

| 请求 | 地址 |
| --- | --- |
| HTTPS | `https://httpbin.org/get?room=A203` |
| HTTP | `http://httpbin.org/get?room=A203` |

两个按钮访问同一路径与参数，只改变协议。程序关闭自动重定向；应以应用中显示的实际状态码判断结果，不能把 HTTP 301/302 或浏览器访问结果当作应用的 HTTP 200。更改 `MainActivity.kt` 中的 `room` 参数后，可再次运行并核对响应中的参数值。

## 网络配置

- `app/src/main/AndroidManifest.xml` 声明 `INTERNET` 权限，并在 `<application>` 上引用 `@xml/network_security_config`。
- `app/src/main/res/xml/network_security_config.xml` 默认禁止明文通信，仅对 `httpbin.org` 单独允许 HTTP；实验中可将该域名的 `cleartextTrafficPermitted` 暂时改为 `false` 观察拦截，再改回 `true` 并重新安装应用。
- `app/src/main/java/com/example/firstkotlinapp/MainActivity.kt` 包含 Compose 页面和网络请求代码。

若出现 `UnknownHostException`，应先检查设备或模拟器的网络与 DNS；这不代表明文策略拦截。若服务返回 404、500 或重定向，也不能记为 HTTP 200。

**HTTP 仅用于教学对比，实际服务优先 HTTPS。**
