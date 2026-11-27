# TwitterKeep

트위터 앱에서 **공유 → TwitterKeep**을 선택하면 공개 게시물에 첨부된 사진, 동영상, GIF를 사진 앱에 저장합니다. 사진은 원본 주소를 이용하고, 동영상과 GIF는 트위터가 제공하는 MP4 파일을 내려받습니다. 대표 영상 주소가 스트리밍 재생목록이면 게시물에 포함된 다른 형식에서 MP4를 찾습니다. 사진과 영상이 섞여 있어도 항목마다 따로 저장합니다.

공개 게시물의 숫자 ID는 [FxTwitter](https://docs.fxembed.com/api/introduction)로 전송됩니다. 미디어 파일은 트위터의 이미지·영상 서버에서 내려받습니다. 비공개·삭제된 게시물, 외부 사이트 영상, MP4 파일 없이 스트리밍으로만 제공되는 영상은 지원 범위에 포함되지 않습니다. 인용 게시물은 공유한 게시물에 직접 첨부된 미디어를 대상으로 합니다.

## Mac이 있으면 단축어 파일로 설치

[서명 전 단축어 파일](TwitterKeep-unsigned.shortcut)을 내려받고, 파일이 있는 폴더에서 아래 명령을 실행합니다.

```sh
shortcuts sign --mode anyone --input TwitterKeep-unsigned.shortcut --output TwitterKeep.shortcut
```

서명된 `TwitterKeep.shortcut`을 아이폰으로 AirDrop하고 **단축어 추가**를 누릅니다. 이름이 파일명으로 표시되면 **TwitterKeep**으로 바꿀 수 있습니다. 트위터 앱에서 공개 게시물의 **공유 → 공유하기… → TwitterKeep**을 누릅니다. 클립보드에 링크를 복사한 후 단축어 앱에서 직접 실행할 수도 있습니다. 처음 실행할 때 요청되는 네트워크와 사진 앱 접근을 허용합니다.

## 아이폰만 있으면 Scriptable로 설치

1. App Store에서 **Scriptable**을 설치합니다. 새 스크립트를 만들고 이름을 **TwitterKeep**으로 정한 뒤, [스크립트 파일](TwitterKeep.scriptable.js)의 전체 내용을 붙여넣습니다.
2. **단축어** 앱에서 **TwitterKeep**이라는 새 단축어를 만듭니다. 세부사항의 **공유 시트에서 보기**를 켜고 입력 유형으로 **URL**과 **텍스트**를 지정합니다.
3. **텍스트** 동작을 추가하고 텍스트 칸에 마법 변수 **단축어 입력**을 넣습니다. 이어서 Scriptable의 **Run Script** 동작을 추가하고 스크립트를 **TwitterKeep**, **Parameter**를 앞의 **텍스트** 결과로 지정합니다.
4. **각 항목 반복** 동작을 추가하고 반복 대상으로 **Run Script** 결과를 지정합니다. 반복 안에 **URL 콘텐츠 가져오기**를 넣고, URL을 **반복 항목**으로 지정합니다. 같은 반복 안에 **사진 앨범에 저장**을 넣고 입력을 **URL 콘텐츠**로 지정합니다.
5. 트위터 앱에서 공개 게시물의 **공유 → 공유하기… → TwitterKeep**을 누릅니다. 처음 실행할 때 요청되는 네트워크와 사진 앱 접근을 허용합니다.

## 단축어 다시 생성

```sh
python3 generate_shortcut.py
```

Apple 서명과 사진 앱에서의 저장은 Apple 기기에서 확인해야 합니다.
