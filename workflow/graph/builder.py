from langgraph.graph import StateGraph, START, END
from workflow.graph.stage import TranslationState
from workflow.node.translate_en_vi import translate_en_vi_node
from workflow.node.rule_check import rule_check_node
from workflow.node.translate_vi_en import translate_vi_en_node
from workflow.node.evaluate import evaluate_node

def check_valid_variants(state: TranslationState):
    """
    Điều hướng có điều kiện (Conditional Routing):
    Nếu không có bản dịch nào sống sót sau khi quét Rule, tiến trình kết thúc ngay.
    Ngược lại, chuyển các bản dịch hợp lệ đi tiếp sang Node Back-translation.
    """
    translated_texts = state.get("translated_texts", [])
    if len(translated_texts) == 0:
        return "end"
    return "continue"

def build_translation_workflow():
    """
    Khởi tạo và biên dịch đồ thị LangGraph cho quy trình dịch thuật và chấm điểm song ngữ.
    """
    workflow = StateGraph(TranslationState)
    
    # Khai báo các Node tham gia vào đồ thị
    workflow.add_node("translate_en_vi", translate_en_vi_node)
    workflow.add_node("rule_check", rule_check_node)
    workflow.add_node("translate_vi_en", translate_vi_en_node)
    workflow.add_node("evaluate", evaluate_node)
    
    # Thiết lập luồng chạy (Edges)
    workflow.add_edge(START, "translate_en_vi")
    workflow.add_edge("translate_en_vi", "rule_check")
    
    # Luồng rẽ nhánh linh hoạt (Conditional Edges)
    workflow.add_conditional_edges(
        "rule_check",
        check_valid_variants,
        {
            "continue": "translate_vi_en",
            "end": END
        }
    )
    
    workflow.add_edge("translate_vi_en", "evaluate")
    workflow.add_edge("evaluate", END)
    
    # Biên dịch Graph thành Runnable App
    app = workflow.compile()
    return app
