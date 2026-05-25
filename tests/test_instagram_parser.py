from src.instagram_parser import extract_shared_reels


def test_extracts_attachment_type_ig_reel():
    payload = {
        "entry": [
            {
                "id": "ig-account-1",
                "messaging": [
                    {
                        "sender": {"id": "sender-1"},
                        "recipient": {"id": "recipient-1"},
                        "message": {
                            "mid": "m-1",
                            "attachments": [
                                {
                                    "type": "ig_reel",
                                    "payload": {
                                        "url": "https://www.instagram.com/reel/ABC123/?utm_source=foo#bar",
                                        "video_id": "video-1",
                                        "title": "Reel title",
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ]
    }

    results = extract_shared_reels(payload)

    assert results == [
        {
            "source_ig_account_id": "ig-account-1",
            "sender_id": "sender-1",
            "recipient_id": "recipient-1",
            "message_id": "m-1",
            "reel_url": "https://www.instagram.com/reel/ABC123/",
            "reel_video_id": "video-1",
            "reel_title": "Reel title",
            "attachment_type": "ig_reel",
        }
    ]


def test_extracts_attachment_type_reel():
    payload = {
        "entry": [
            {
                "id": "ig-account-1",
                "messaging": [
                    {
                        "sender": {"id": "sender-1"},
                        "recipient": {"id": "recipient-1"},
                        "message": {
                            "mid": "m-2",
                            "attachments": [
                                {
                                    "type": "reel",
                                    "payload": {
                                        "url": "https://instagram.com/reel/XYZ789/?foo=bar",
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ]
    }

    results = extract_shared_reels(payload)

    assert results[0]["attachment_type"] == "reel"
    assert results[0]["reel_url"] == "https://instagram.com/reel/XYZ789/"


def test_extracts_shares_data_link():
    payload = {
        "entry": [
            {
                "id": "ig-account-1",
                "messaging": [
                    {
                        "sender": {"id": "sender-1"},
                        "recipient": {"id": "recipient-1"},
                        "message": {
                            "mid": "m-3",
                            "shares": {
                                "data": [
                                    {
                                        "link": "https://www.instagram.com/reel/SHARE01/?igsh=abc",
                                        "id": "share-video-1",
                                        "title": "Shared reel",
                                    }
                                ]
                            },
                        },
                    }
                ],
            }
        ]
    }

    results = extract_shared_reels(payload)

    assert results == [
        {
            "source_ig_account_id": "ig-account-1",
            "sender_id": "sender-1",
            "recipient_id": "recipient-1",
            "message_id": "m-3",
            "reel_url": "https://www.instagram.com/reel/SHARE01/",
            "reel_video_id": "share-video-1",
            "reel_title": "Shared reel",
            "attachment_type": "share_link",
        }
    ]


def test_extracts_text_url():
    payload = {
        "entry": [
            {
                "id": "ig-account-1",
                "messaging": [
                    {
                        "sender": {"id": "sender-1"},
                        "recipient": {"id": "recipient-1"},
                        "message": {
                            "mid": "m-4",
                            "text": "Check this reel https://www.instagram.com/reel/TEXT42/?utm_source=ig_web_copy_link",
                        },
                    }
                ],
            }
        ]
    }

    results = extract_shared_reels(payload)

    assert results == [
        {
            "source_ig_account_id": "ig-account-1",
            "sender_id": "sender-1",
            "recipient_id": "recipient-1",
            "message_id": "m-4",
            "reel_url": "https://www.instagram.com/reel/TEXT42/",
            "reel_video_id": None,
            "reel_title": None,
            "attachment_type": "text_url",
        }
    ]


def test_removes_query_string_and_fragment():
    payload = {
        "entry": [
            {
                "id": "ig-account-1",
                "messaging": [
                    {
                        "sender": {"id": "sender-1"},
                        "recipient": {"id": "recipient-1"},
                        "message": {
                            "mid": "m-5",
                            "text": "https://www.instagram.com/reel/ABCDEF/?a=1#frag",
                        },
                    }
                ],
            }
        ]
    }

    results = extract_shared_reels(payload)

    assert results[0]["reel_url"] == "https://www.instagram.com/reel/ABCDEF/"


def test_rejects_non_instagram_domains():
    payload = {
        "entry": [
            {
                "messaging": [
                    {
                        "message": {
                            "mid": "m-6",
                            "text": "https://example.com/reel/ABC123/",
                        }
                    }
                ]
            }
        ]
    }

    assert extract_shared_reels(payload) == []


def test_rejects_instagram_paths_that_are_not_reel():
    payload = {
        "entry": [
            {
                "messaging": [
                    {
                        "message": {
                            "mid": "m-7",
                            "text": "https://www.instagram.com/p/ABC123/",
                        }
                    }
                ]
            }
        ]
    }

    assert extract_shared_reels(payload) == []


def test_deduplicates_same_message_id_and_reel_url():
    payload = {
        "entry": [
            {
                "id": "ig-account-1",
                "messaging": [
                    {
                        "sender": {"id": "sender-1"},
                        "recipient": {"id": "recipient-1"},
                        "message": {
                            "mid": "m-8",
                            "text": "https://www.instagram.com/reel/DEDUP1/",
                            "shares": {
                                "data": [
                                    {
                                        "link": "https://www.instagram.com/reel/DEDUP1/?a=1",
                                    }
                                ]
                            },
                        },
                    }
                ],
            }
        ]
    }

    results = extract_shared_reels(payload)

    assert len(results) == 1
    assert results[0]["reel_url"] == "https://www.instagram.com/reel/DEDUP1/"


def test_returns_empty_list_for_malformed_payload():
    assert extract_shared_reels({"entry": "not-a-list"}) == []
    assert extract_shared_reels(None) == []


def test_returns_empty_list_when_mid_is_missing():
    payload = {
        "entry": [
            {
                "messaging": [
                    {
                        "message": {
                            "text": "https://www.instagram.com/reel/NO-MID/",
                        }
                    }
                ]
            }
        ]
    }

    assert extract_shared_reels(payload) == []

