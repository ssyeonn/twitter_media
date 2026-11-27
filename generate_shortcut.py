#!/usr/bin/env python3
"""Build the unsigned XKeep workflow for Apple Shortcuts."""

import plistlib
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

API = "https://api.fxtwitter.com/2/status/"
POST = (
    r"(?i)https://(?:(?:www|mobile|m)\.)?(?:x|twitter)\.com/"
    r"(?:i/web|[a-z0-9_]{1,15})/status/[0-9]{1,20}(?![a-z0-9_])"
)
PHOTO = r"(?i)^https://pbs\.twimg\.com/media/[^\s]+$"
MP4 = r"(?i)^https://video\.twimg\.com/[^?\s#]+\.mp4(?:\?[^\s#]*)?$"
NO_MEDIA = "저장할 사진이나 MP4 영상을 찾지 못했어요. 공개 게시물인지 확인해 주세요."


def attachment(value):
    return {"Value": value, "WFSerializationType": "WFTextTokenAttachment"}


def text_token(prefix, value, suffix=""):
    return {
        "Value": {
            "string": f"{prefix}\ufffc{suffix}",
            "attachmentsByRange": {f"{{{len(prefix.encode('utf-16-le')) // 2}, 1}}": value},
        },
        "WFSerializationType": "WFTextTokenString",
    }


def variable(name):
    return {"Type": "Variable", "VariableName": name}


class Workflow:
    def __init__(self):
        self.actions = []

    def add(self, identifier, **parameters):
        action = {"WFWorkflowActionIdentifier": f"is.workflow.actions.{identifier}"}
        if parameters:
            action["WFWorkflowActionParameters"] = parameters
        self.actions.append(action)

    def output(self, identifier, name, **parameters):
        uid = str(uuid4())
        self.add(identifier, UUID=uid, CustomOutputName=name, **parameters)
        return {"Type": "ActionOutput", "OutputUUID": uid, "OutputName": name}

    @contextmanager
    def block(self, identifier, **parameters):
        group = str(uuid4())
        self.add(identifier, GroupingIdentifier=group, WFControlFlowMode=0, **parameters)
        yield
        self.add("nothing")
        self.add(identifier, GroupingIdentifier=group, WFControlFlowMode=2, UUID=group)

    def condition(self, value, has_value):
        return self.block(
            "conditional",
            WFInput={"Type": "Variable", "Variable": attachment(value)},
            WFCondition=100 if has_value else 101,
        )

    def alert(self, message):
        self.add(
            "alert",
            WFAlertActionTitle="엑스킵",
            WFAlertActionMessage=message,
            WFAlertActionCancelButtonShown=False,
        )

    def require(self, value, message):
        with self.condition(value, False):
            self.alert(message)
            self.add("exit")

    def match(self, source, pattern, name):
        return self.output("text.match", name, WFMatchTextPattern=pattern,
                           text=text_token("", source))

    def first(self, source, name):
        return self.output("getitemfromlist", name, WFInput=attachment(source),
                           WFItemSpecifier="First Item")

    def get(self, source, key, name):
        return self.output("getvalueforkey", name, WFInput=attachment(source),
                           WFGetDictionaryValueType="Value", WFDictionaryKey=key)

    def fetch(self, url, name):
        return self.output("downloadurl", name, WFURL=url, WFHTTPMethod="GET")

    def set(self, name, value):
        self.add("setvariable", WFInput=attachment(value), WFVariableName=name)


def build():
    flow = Workflow()
    source = {"Type": "ExtensionInput", "VariableName": "ShortcutInput"}
    matches = flow.match(source, POST, "게시물 링크")
    flow.require(matches, "공개 X 게시물 링크를 공유하거나 클립보드에 복사해 주세요.")
    link = flow.first(matches, "첫 게시물 링크")
    ids = flow.match(link, r"[0-9]+$", "게시물 ID")
    post_id = flow.first(ids, "첫 게시물 ID")

    response = flow.fetch(text_token(API, post_id), "API 응답")
    result = flow.output("detect.dictionary", "응답 사전", WFInput=attachment(response))
    status = flow.get(result, "status", "게시물")
    flow.require(status, NO_MEDIA)
    media = flow.get(status, "media", "미디어 사전")
    flow.require(media, NO_MEDIA)
    items = flow.get(media, "all", "미디어 목록")
    flow.require(items, NO_MEDIA)

    selected = "선택한 미디어"
    saved = "저장한 파일"
    with flow.block("repeat.each", WFInput=attachment(items)):
        item = flow.output("detect.dictionary", "미디어 항목",
                           WFInput=attachment(variable("Repeat Item")))
        url = flow.get(item, "url", "대표 주소")
        kind = flow.get(item, "type", "미디어 유형")
        photos = flow.match(kind, r"^photo$", "사진 여부")
        # Every iteration resets the candidate. A video thumbnail is not a candidate.
        videos = flow.match(url, MP4, "대표 MP4")
        flow.set(selected, videos)

        with flow.condition(photos, True):
            flow.set(selected, flow.match(url, PHOTO, "원본 사진"))

        with flow.condition(photos, False):
            with flow.condition(variable(selected), False):
                formats = flow.get(item, "formats", "영상 형식")
                with flow.condition(formats, True):
                    with flow.block("repeat.each", WFInput=attachment(formats)):
                        with flow.condition(variable(selected), False):
                            variant = flow.output("detect.dictionary", "영상 형식 항목",
                                                  WFInput=attachment(variable("Repeat Item 2")))
                            variant_url = flow.get(variant, "url", "영상 형식 주소")
                            mp4 = flow.match(variant_url, MP4, "대체 MP4")
                            with flow.condition(mp4, True):
                                flow.set(selected, mp4)

        with flow.condition(variable(selected), True):
            media_url = flow.first(variable(selected), "다운로드 주소")
            file = flow.fetch(text_token("", media_url), "미디어 파일")
            flow.add("savetocameraroll", WFInput=attachment(file))
            flow.add("appendvariable", WFInput=attachment(media_url), WFVariableName=saved)

    flow.require(variable(saved), NO_MEDIA)
    count = flow.output("count", "저장 개수", Input=attachment(variable(saved)))
    flow.alert(text_token("사진 앱에 ", count, "개 파일을 저장했어요."))

    return {
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowClientVersion": "1505.3",
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 3679049983,
            "WFWorkflowIconGlyphNumber": 61440,
        },
        "WFWorkflowOutputContentItemClasses": [],
        "WFWorkflowHasOutputFallback": False,
        "WFWorkflowNoInputBehavior": {"Name": "WFWorkflowNoInputBehaviorGetClipboard"},
        "WFWorkflowActions": flow.actions,
        "WFWorkflowInputContentItemClasses": ["WFStringContentItem", "WFURLContentItem"],
        "WFWorkflowImportQuestions": [],
        "WFWorkflowTypes": ["ActionExtension"],
        "WFQuickActionSurfaces": [],
        "WFWorkflowHasShortcutInputVariables": True,
    }


if __name__ == "__main__":
    output = Path(__file__).with_name("XKeep-unsigned.shortcut")
    output.write_bytes(plistlib.dumps(build(), fmt=plistlib.FMT_BINARY))
