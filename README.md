# E-paper-Calendar

Calendar created with Waveshare 7.5inch e-paper and RaspberryPi zero.

RaspberryPiと Waveshare e-paper 7.5inchを使用して予定表を表示する

<p align="center">
<img src="https://github.com/9610r/e-paperCalendar/blob/master/images/sample_image1.jpg" width="640">
</p>


https://github.com/mktia/e-calendar

こちらのプロジェクトが素晴らしかったので, 自分用に改変

## Usage

- RaspberryPi zero WH (RaspberryPi OS lite)
- [7.5inch e-Paper HAT - Waveshare Wiki](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT)

```zsh
$ git clone https://github.com/mktia/e-calendar.git && cd ./e-calendar

```

```sh
$ sudo pip install google-api-python-client
$ sudo pip install google-auth-httplib2
$ sudo pip install google-auth-oauthlib

$ sudo pip install pillow
$ sudo pip install RPi.GPIO
$ sudo pip install spidev
```

Waveshare製 7.5inch V2 以外のWaveshare製電子ペーパーを使用する場合は以下のプロジェクトの
`e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd/`から該当する製品のライブラリを取得して`epd7in5_V2.py`と置き換える必要があります。

https://github.com/waveshare/e-Paper


## Example

組み込む前に表示用画像(800*480)を生成して確認することができます。

Experiment with a sample program to obtain images (800x480) to be displayed on e-paper.

```python
python3 create_image.py
```



## License
Copyright (c) 2022 tiger
Copyright (c) 2021 mktia.

This software is released under the MIT License, see LICENSE.
