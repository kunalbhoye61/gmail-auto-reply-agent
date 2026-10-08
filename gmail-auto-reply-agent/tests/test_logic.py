from gmail_agent import agent, config


def test_should_ignore_noreply():
    assert agent.should_ignore("NoReply@example.com") is True  # case-insensitive
    assert agent.should_ignore("noreply@example.com") is True
    assert agent.should_ignore("friend@example.com") is False


def test_decide_action_draft_only(monkeypatch):
    monkeypatch.setattr(config, "AUTO_SEND_MODE", "draft_only")
    assert agent.decide_action("anyone@example.com") == "draft"


def test_decide_action_whitelist(monkeypatch):
    monkeypatch.setattr(config, "AUTO_SEND_MODE", "whitelist")
    monkeypatch.setattr(config, "AUTO_SEND_WHITELIST", ["@kkwagh.edu.in"])
    assert agent.decide_action("prof@kkwagh.edu.in") == "send"
    assert agent.decide_action("stranger@gmail.com") == "draft"


def test_decide_action_all(monkeypatch):
    monkeypatch.setattr(config, "AUTO_SEND_MODE", "all")
    assert agent.decide_action("anyone@example.com") == "send"
