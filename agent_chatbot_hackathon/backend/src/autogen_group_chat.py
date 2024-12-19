import autogen
import autogen
from autogen import UserProxyAgent
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from autogen.function_utils import get_function_schema
from autogen import Agent

from user_proxy_webagent import UserProxyWebAgent
from groupchatweb import GroupChatManagerWeb
import asyncio

config_list = [
    {
        "model": "gpt-4o",
    }
]
llm_config_assistant = {
    "model": "gpt-4o",
    "temperature": 0,
    "config_list": config_list,
}
llm_config_proxy = {
    "model": "gpt-4o",
    "temperature": 0,
    "config_list": config_list,
}


def save_user_details(name: str, mobile: str, email: str, age: int) -> str:
    """
    Save user details in the database to register a new user

    Parameters:
    - name: Name of the user.
    - mobile: mobile number of the user.
    - email: email of the user.
    - age: age of the user

    Returns:
    Success/Failure.
    """
    print(f"{name}\t {mobile}\t{email}\t{age}")
    return "Success"


def save_user_target(name: str, target: str) -> str:
    """
    Save user details in the database to register a new user

    Parameters:
    - name: Name of the user.
    - target: target of the user.
    Returns:
    Success/Failure.
    """
    print(f"{name}\t {target}")
    return "Success"


# Assistant API Tool Schema for saving uer details
get_save_user_details = get_function_schema(
    save_user_details,
    name="save_user_details",
    description="Save the user details in the system",
)

# Assistant API Tool Schema for saving uer details
get_save_user_details = get_function_schema(
    save_user_details,
    name="save_user_details",
    description="Save the user details in the system",
)

# Assistant API Tool Schema for saving user target details
get_save_user_target = get_function_schema(
    save_user_target,
    name="save_user_target",
    description="Save the user target details in the system",
)


#############################################################################################
# this is where you put your Autogen logic, here I have a simple 2 agents with a function call
class AutogenChat():
    def __init__(self, chat_id=None, websocket=None):
        self.websocket = websocket
        self.chat_id = chat_id
        self.client_sent_queue = asyncio.Queue()
        self.client_receive_queue = asyncio.Queue()

        self.receptionist_agent = GPTAssistantAgent(
            name="receptionist_agent",
            instructions="""
    You are the receptionist at Pathway Services Ltd., this organisation helps the people
    in achieving their goals for learning. These goals can be any job preparation, exam preparation.
    You have following points to take care: 1. Register new users, details needed to register are Name, mobile, email 
    and age. You need to save the information using save_user_detail function.
    2. Share information about the company and how can our company help in achieving their targets.
    """,
            overwrite_instructions=True,  # overwrite any existing instructions with the ones provided
            overwrite_tools=True,  # overwrite any existing tools with the ones provided
            llm_config={
                "config_list": config_list,
                "tools": [get_save_user_details],
            },
            code_execution_config={"work_dir": "coding", "use_docker": False}
        )

        # self.creator = autogen.AssistantAgent(
        #     name="creator",
        #     llm_config=llm_config_assistant,
        #     max_consecutive_auto_reply=5,
        #     system_message="""You are a helpful assistant, you have creative ideas"""
        # )
        # self.critic = autogen.AssistantAgent(
        #     name="critic",
        #     llm_config=llm_config_assistant,
        #     max_consecutive_auto_reply=5,
        #     system_message="""You are a helpful assistant, you should validade the ideas from the creator, once done return the idea with the word TERMINATE at the end to the user"""
        # )

        self.user_proxy = UserProxyWebAgent(
            name="user_proxy",
            human_input_mode="ALWAYS",
            system_message="""You ask for ideas for a specific topic""",
            max_consecutive_auto_reply=5,
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
        )

        self.receptionist_agent.register_function(
            function_map={
                "save_user_details": save_user_details,
            },
        )

        self.target_agent = GPTAssistantAgent(
            name="target_agent",
            instructions="""
            You are an Executive at Pathway Services Ltd.
            You have following points to take care: 
            1. Once the user is register, Ask for the target that user wants to achieve.
            2. If User is not certain then give him options and help him in selecting the target.
            3. The target finalized with user should be concreate like a programing language or a skill set
            4. Confirm the target with user
            5. Save the user target using save_user_target function.
            """,
            overwrite_instructions=True,  # overwrite any existing instructions with the ones provided
            overwrite_tools=True,  # overwrite any existing tools with the ones provided
            llm_config={
                "config_list": config_list,
                "tools": [get_save_user_target],
            },
            code_execution_config={"work_dir": "coding", "use_docker": False}
        )

        self.target_agent.register_function(
            function_map={
                "save_user_target": save_user_target,
            },
        )

        self.teacher_agent = autogen.ConversableAgent(
            name="Teacher",
            system_message="You are a Teacher at Pathway Guider Company. "
                           "Your will interact with user, once the user is **registered** and target is set for the user."
                           "You need to clear the concept of student. "
                           "You use socratic  methods to solve any concept and query of the students"
                           "Main idea is to cross question the student so that he can learn the concept."
                           "Ask question about the concept in the end.",
            description="Teacher, Welcome the user.",
            llm_config=config_list[0]
        )
        # add the queues to communicate
        self.user_proxy.set_queues(self.client_sent_queue, self.client_receive_queue)

        self.groupchat = autogen.GroupChat(agents=[self.user_proxy,
                                                   self.receptionist_agent,
                                                   self.target_agent,
                                                   self.teacher_agent],
                                           messages=[],
                                           max_round=20,
                                           speaker_selection_method=self.custom_speaker_selection_func)
        self.manager = GroupChatManagerWeb(groupchat=self.groupchat,
                                           llm_config=llm_config_assistant,
                                           human_input_mode="ALWAYS",
                                           code_execution_config={"work_dir": "coding", "use_docker": False})

    def custom_speaker_selection_func(self, last_speaker: Agent, groupchat: autogen.GroupChat):
        """Define a customized speaker selection function.
        A recommended way is to define a transition for each speaker in the groupchat.

        Returns:
            Return an `Agent` class or a string from ['auto', 'manual', 'random', 'round_robin'] to select a default method to use.
        """
        messages = groupchat.messages

        if len(messages) <= 1:
            return self.receptionist_agent
        return 'auto'

    async def start(self, message):
        await self.user_proxy.a_initiate_chat(
            self.manager,
            clear_history=True,
            message=message
        )
