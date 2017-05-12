# -*- coding: utf-8 -*-

import text_process as tp
import platform
from snownlp import SnowNLP
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class Dictionary:

    def __init__(self):
        # 初始化化路径
        self.POS_DICT_PATH = '\\dictionary\\emotion_dict\\pos_dict_pmi.txt'
        self.NEG_DICT_PATH = '\\dictionary\\emotion_dict\\neg_dict_pmi.txt'
        self.KEY_WORDS_PATH = '\\dictionary\\emotion_dict\\key_words.txt'
        self.INVERSE_DICT_PATH = '\\dictionary\\degree_dict\\inverse.txt'
        self.ISH_DICT_PATH = '\\dictionary\\degree_dict\\ish.txt'
        self.MORE_DICT_PATH = '\\dictionary\\degree_dict\\more.txt'
        self.VERY_DICT_PATH = '\\dictionary\\degree_dict\\very.txt'
        self.MOST_DICT_PATH = '\\dictionary\\degree_dict\\most.txt'
        self.STOP_WORDS_PATH = '\\dictionary\\emotion_dict\\stop_words.txt'

        # 修正路径格式
        self.check_path()

        # 导入字典
        self.pos_dict = tp.loadDict(self.POS_DICT_PATH)
        self.neg_dict = tp.loadDict(self.NEG_DICT_PATH)
        self.key_words = tp.read_file(self.KEY_WORDS_PATH)
        self.inverse_dict = tp.read_file(self.INVERSE_DICT_PATH)  # weight -1
        self.ish_dict = tp.read_file(self.ISH_DICT_PATH)  # weight 0.5
        self.more_dict = tp.read_file(self.MORE_DICT_PATH)  # weight 1.5
        self.very_dict = tp.read_file(self.VERY_DICT_PATH)  # weight 1.75
        self.most_dict = tp.read_file(self.MOST_DICT_PATH)  # weight 2
        self.stop_words_dict = tp.read_file(self.STOP_WORDS_PATH)

        # 定义权重
        self._weight_inverse = -1.0
        self._weight_ish = 0.5
        self._weight_more = 1.5
        self._weight_very = 1.75
        self._weight_most = 2.0
        self._weight_key_word = -200

    def check_path(self):
        # 获得Linux文件路径
        if 'Windows' not in platform.system():
            self.POS_DICT_PATH = self.POS_DICT_PATH.replace('\\', '/')
            self.NEG_DICT_PATH = self.NEG_DICT_PATH.replace('\\', '/')
            self.KEY_WORDS_PATH = self.KEY_WORDS_PATH.replace('\\', '/')
            self.INVERSE_DICT_PATH = self.INVERSE_DICT_PATH.replace('\\', '/')
            self.ISH_DICT_PATH = self.ISH_DICT_PATH.replace('\\', '/')
            self.MORE_DICT_PATH = self.MORE_DICT_PATH.replace('\\', '/')
            self.VERY_DICT_PATH = self.VERY_DICT_PATH.replace('\\', '/')
            self.MOST_DICT_PATH = self.MOST_DICT_PATH.replace('\\', '/')
            self.STOP_WORDS_PATH = self.STOP_WORDS_PATH.replace('\\', '/')

    @property
    def weight_inverse(self):
        return self._weight_inverse

    @property
    def weight_key_word(self):
        return self._weight_key_word

    @property
    def weight_ish(self):
        return self._weight_ish

    @property
    def weight_more(self):
        return self._weight_more

    @property
    def weight_very(self):
        return self._weight_very

    @property
    def weight_most(self):
        return self._weight_most

    def del_stop_words(self, words):
        new_words = []
        for word in words:
            if word not in self.stop_words_dict:
                new_words.append(word)
        return new_words

    def SnowNLP_analyze(self, content):
        # print content
        s = SnowNLP(content)
        ratio = s.sentiments
        # 0.45--0.7认定为中性
        if ratio > 0.7:
            return 0.5
        elif ratio < 0.45:
            return -0.5
        else:
            return 0.0

    def calculate_score(self, content):
        total_score = 0.0
        cut_contexts = tp.cut_sentence(content)
        isKeyWord = False
        # 对应每句话
        # print 'content: ', content
        for cut_context in cut_contexts:
            words = tp.segmentation(cut_context)
            # 去停用词
            words = self.del_stop_words(words)
            score = 0.0
            prefix = 1.0
            for word in words:
                if word in self.inverse_dict:
                    prefix *= self.weight_inverse
                    # print "inverse word:", word, self.weight_inverse
                elif word in self.ish_dict:
                    prefix *= self.weight_ish
                    # print "ish word", word, self.weight_ish
                elif word in self.more_dict:
                    prefix *= self.weight_more
                    # print "more word:", word, self.weight_more
                elif word in self.very_dict:
                    prefix *= self.weight_very
                    # print "very word:", word, self.weight_very
                elif word in self.most_dict:
                    prefix *= self.weight_most
                    # print "most word", word, self.weight_most
                # if len(word) >= 2:
                else:
                    result, flag = self.word_search(word)
                    if flag:
                        score += result
                    if word in self.key_words:
                        isKeyWord = True
                        # print 'key',word
                # print 'word:', word, score
            score_final = prefix * score
            # print 'sentence:', cut_context, score_final, prefix
            # if (score_final > -0.001) & (score_final < 0.001):
            #     score_final = self.SnowNLP_analyze(cut_context)
            # print "final_socre",score_final
            total_score += score_final
            # print 'total score:', total_score
        if isKeyWord & (total_score < -0.01):
            total_score += self.weight_key_word
        return total_score

    def sentiment_analyze(self, content):
        result = self.calculate_score(content)
        label = 0
        if result > 2.0:
            label = 1
        elif result > -0.01:
            label = 0
        else:
            label = -1
        return label, result

    # 计算每个单词在字典中的得分
    def word_search(self, word):
        result = self.search(word)
        if result < 999.9:
            return result, True
        else:
            return 0.0, False

    def search(self, word):
        for posWord in self.pos_dict:
            if posWord[0] == word:
                return posWord[1]
        for negWord in self.neg_dict:
            if negWord[0] == word:
                return negWord[1]
        return 999.9


if __name__ == '__main__':
    print 'test'
    dic = Dictionary()
    print dic.calculate_score('近日，“小学出现大尺度性教育读物”引起争议。校方称，这批书本意是为了教导孩子学会保护自己，因在五六年级课程效果较好，于是采用了“图书漂流”的方式，最终“漂”到二年级学生手中。事先未与家长沟通，才造成误会。目前校方决定先收回该批书。(3月5日《北京青年报》)这起事件的最新进展是，校方已经决定先收回这些读本，也就意味着，小学生今后不会再接触到这些读本，这显然不是解决问题的办法，也不利于小学生正常的性教育。小学生的性教育从来都不缺教材，缺的是正规的教育方式，换而言之，“大尺度”可以有，但必须多花“小心思"。长期以来，在小学生性教育过程，一直存在着这样一个问题：重教材轻教育。虽然有很多这方面的教材，但是老师在对学生进行性教育的过程中，往往存在着教育和引导的缺失，很多老师在进行性教育时，不是对这些教学内容一笔带过、点到为止，就是要求学生进行自学，自己翻阅书籍，了解性教育知识，这显然不是一种正确的教学方式，出现这种现象的主要原因是，一方面，一些老师对性教育缺乏正确认识，在教学时，不能正确面对，羞于启齿，谈性色变，性教育匆匆而过，一方面缘于老师对性教育的不重视，性教育只是一种副科，不参与考试，或者在考试中占据的比例很小，导致一些老师在教学中厚此薄彼，只注重语数英等主科，而忽略了性教育，殊不知这是一种错误的认识，与那些主科相比，性教育更为重要，不仅关系着学生树立正确的性观念，甚至影响着今后的性道德。让学生自行学习固然可以，但是如果老师闭口不谈，含糊其辞，草草了之，学生又如何会重视？学生不重视，又如何确保性教育效果。再者，没有老师的引导和讲解，学生的理解必然千差万别，一些疑问和疑惑得不到科学的解答，导致一知半解，这不仅不利于学生健康成长，反而会增加学生的好奇心，甚至可能出现通过其他途径获得性知识的结果，这就给学生误入歧途埋下伏笔。这也是长期以来，很多地方在地学生进行性教育的一种现象。此次事件也是这样，虽然只是课外读本，但是学校只是发给学生，让学生自行学习，既没有组织专门的教育，也没有和家长沟通，加强对学生的引导，只提供教材，没有提供教育，如何保证学习效果，这就导致了学生站在学习中出现混乱的现象，这也是家长吐槽的原因之一。可见，性教育缺少的不是教材，而是教育。在教材方面，我们有适合各个年龄段的性教育教材，但是教育中却存在着巨大的缺失，在教学过程中，这些教材却没有很好地被使用和利用，甚至沦为摆设，成为学生自习的课外书籍，没有起到应有的教育效果，这样的教育现状，显然是值得警醒的。虽然决定收回这些教材，但是对学生的性教育却不能停止。小学正是性教育的关键时期，这个时期，老师应该大大方方地进行性教育，深入细致的讲解科学的生理知识，为学生补上性教育课，引导学生正确认识生理变化，加强自我保护，引导学生健康成长。')
