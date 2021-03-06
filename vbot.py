# import config
#
# from flask import Flask, request, Response
# from viberbot import Api
# from viberbot.api.bot_configuration import BotConfiguration
# from viberbot.api.messages import VideoMessage
# from viberbot.api.messages.text_message import TextMessage
# import logging
#
# from viberbot.api.viber_requests import ViberConversationStartedRequest
# from viberbot.api.viber_requests import ViberFailedRequest
# from viberbot.api.viber_requests import ViberMessageRequest
# from viberbot.api.viber_requests import ViberSubscribedRequest
# from viberbot.api.viber_requests import ViberUnsubscribedRequest
#
# app = Flask(__name__)
# viber = Api(BotConfiguration(
#     name='HelpLearnEnglishBot',
#     avatar='s1_1497952242.jpg',
#     auth_token=config.token_viber
# ))
#
#
# @app.route('/', methods=['POST'])
# def incoming():
#     logger = logging.getLogger()
#     logger.setLevel(logging.DEBUG)
#     handler = logging.StreamHandler()
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)
#
#
#     logger.debug("received request. post data: {0}".format(request.get_data()))
#     # every viber message is signed, you can verify the signature using this method
#     if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
#         return Response(status=403)
#
#     # this library supplies a simple way to receive a request object
#     viber_request = viber.parse_request(request.get_data())
#
#     if isinstance(viber_request, ViberMessageRequest):
#         message = viber_request.message
#         # lets echo back
#         viber.send_messages(viber_request.sender.id, [
#             message
#         ])
#     elif isinstance(viber_request, ViberSubscribedRequest):
#         viber.send_messages(viber_request.get_user.id, [
#             TextMessage(text="thanks for subscribing!")
#         ])
#     elif isinstance(viber_request, ViberFailedRequest):
#         logger.warn("client failed receiving message. failure: {0}".format(viber_request))
#
#     return Response(status=200)
#
#
# if __name__ == "__main__":
#     context = ('server.crt', 'server.key')
#     app.run(host='127.0.0.1', port=443, debug=False, ssl_context=context)
