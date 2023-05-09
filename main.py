def docNormalization(doc: str) -> str:
    return ''.join([c.lower() for c in list(doc) if c.isalpha() or c.isspace()])

def expNormalization(exp: str) -> str:
    exp = ''.join([c.lower() for c in exp if c.isalpha() or c.isspace() or c in ['!','(',')','&','|']])
    exp = ''.join([c.lower() if c.isalpha() else f' {c} ' if not c.isspace() else '' for c in exp])
    exp = ' '.join(exp.split())
    return exp

def notOpBool(l:list[bool]) -> list[bool]:
    return list(map(lambda x: not x,l))

def andOpBool(l1:list[bool], l2:list[bool]) -> list[bool]:
    return [l1[i] and l2[i] for i in range(len(l1))]

def orOpBool(l1:list[bool], l2:list[bool]) -> list[bool]:
    return [l1[i] or l2[i] for i in range(len(l1))]

def notOpInverted(l:list[int],nDocs:int) -> list[int]:
    docs = [i for i in range(1,nDocs+1)]
    res = [i for i in docs if i not in l]
    return res

def andOpInverted(l1:list[int],l2:list[int]) -> list[int]:
    res = []
    i = j = 0
    if len(l1) < len(l2):
        while i < len(l1) and j < len(l2):
            if l1[i] == l2[j]:
                res.append(l1[i])
                i += 1
                j += 1
            else:
                j += 1
    else:
        while i < len(l1) and j < len(l2):
            if l1[i] == l2[j]:
                res.append(l1[i])
                i += 1
                j += 1
            else:
                i += 1
    return res

def orOpInverted(l1:list[int],l2:list[int]) -> list[int]:
    res = l1.copy()
    for i in l2:
        if i not in res:
            res.append(i)
    res.sort()
    return res

def infix2postfix(exp:str) -> str:
    precedence = {
        '(':3,
        '!':2,
        '&':1,
        '|':0
    }
    stack = []
    infix = exp.split()
    postfix = ''
    for ele in infix:
        if ele.isalpha():
            postfix += ' ' + ele
        if ele in ['!','&','|','(']:
            while stack and precedence[stack[-1]] >= precedence[ele] and stack[-1] != '(':
                postfix += ' ' + stack.pop()
            stack.append(ele)
        if ele == ')':
            while stack and stack[-1] != '(':
                postfix += ' ' + stack.pop()
            stack.pop()
    while stack:
        postfix += ' ' + stack.pop()
    return postfix.strip()

def expresionEval(terms: dict[str:list[bool|int]],exp: str,choice: int,nDocs:int = -1) -> list[bool]:
    exp = exp.split()
    stack = []
    for ele in exp:
        if ele.isalpha():
            stack.append(terms[ele])
        elif ele == '!':
            last = stack.pop()
            stack.append(notOpBool(last) if choice == 1 else notOpInverted(last,nDocs))
        else:
            last1 = stack.pop()
            last2 = stack.pop()
            stack.append((andOpBool(last1,last2) if ele == '&' else orOpBool(last1,last2)) if choice == 1 else (andOpInverted(last1,last2) if ele == '&' else orOpInverted(last1,last2)))
    return stack[-1]


def booleanRetrieval(docs: list[str],exp: str) -> list[bool]:
    booleanMatrix = dict()
    nDocs = len(docs)
    for docId,doc in enumerate(docs):
        for term in doc.split():
            booleanMatrix.setdefault(term,[0]*nDocs)
            booleanMatrix[term][docId] = 1
    terms = dict()
    for ele in exp.split():
        if ele.isalpha():
            terms[ele] = booleanMatrix[ele] if booleanMatrix.get(ele) else [0]*nDocs
    res = expresionEval(terms,exp,1)
    return res

def invertedIndx(docs: list[str],exp: str,nDocs:int = -1) -> list[int]:
    from collections import defaultdict
    posting = defaultdict(set)
    for docId,doc in enumerate(docs,1):
        for term in doc.split():
            posting[term].add(docId)
    for term in posting:
        posting[term] = sorted(posting[term])
    posting = dict(sorted(posting.items()))
    res = expresionEval(posting,exp,2,nDocs)
    return res



def main() -> None:
    print('\nWelcome to our search engine!\n')
    while (nDocs := input('Enter number of documents you want to search in (q to exit): ').strip()) != 'q':
        if not nDocs.isdecimal():
            print('Invalid input try again!')
            continue
        docs = [input(f'Enter document {i+1}: ').strip() for i in range(int(nDocs))]
        docs = [docNormalization(d) for d in docs]
        expresion = input('Enter your query: ').strip()
        expresion = infix2postfix(expNormalization(expresion))
        while (choice := input('Enter 1 for Boolean Retrieval or 2 for Inverted Index: ').strip()) not in ('1','2'):
            print('Invalid input try agian!')
        if choice == '1':
            res = booleanRetrieval(docs,expresion)
            for id,val in enumerate(res,1):
                if val:
                    print(f'Query is found in Doc{id}')
        else:
            res = invertedIndx(docs,expresion,int(nDocs))
            for val in res:
                print(f'Query found in Doc{val}')
        

if __name__ == '__main__':
    main()

