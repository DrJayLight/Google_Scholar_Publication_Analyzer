__author__ = 'jarethmoyo'
import urllib2
from bs4 import BeautifulSoup
from Tkinter import*
import ttk
import re
import clusters
from tkMessageBox import *

result_tuple=()

class GoogleScholarFetcher:

    def __init__(self,url):
        self.url=url

    def fetch(self):
        global result_tuple
        main_author=''
        counter=1
        main_url=self.url.split('citations')[0]
        result_list=[]  # A list of tuples
        all_links=[]
        c=urllib2.urlopen(self.url)
        soup=BeautifulSoup(c.read())
        #First find the main author
        ma=soup.find_all('div',{'id':'gsc_prf_in'})
        for item in ma:
            main_author=item.text
        #this is to find all the links that we will later parse
        links=soup.find_all('tr',{'class': 'gsc_a_tr'})
        for link in links:
            temp_link=link.find_all('a')
            rel_link=temp_link[0].get('href')
            #At this stage we have the relative links.
            #Now to create the actual links
            act_link=main_url+rel_link
            all_links.append(act_link)
        #We will now open each link and extract the relevant data from it
        for link in all_links:
            c2=urllib2.urlopen(link)
            soup2=BeautifulSoup(c2.read())
            titles=soup2.find_all('div',{'class':'gs_scl'})
            tit_names=[]
            tit_vals=[]
            for el in titles:
                headings=el.find_all('div',{'class':'gsc_field'})
                vals=el.find_all('div',{'class':'gsc_value'})
                for el in headings:
                    var=el.text
                    tit_names.append(var)
                for el in vals:
                    #print el
                    q=el.find_all('div',{'id':'gsc_graph'})
                    if len(q)!=0:
                        t1=el.text
                        t2=''
                        #this is to extract only the part of text we need
                        for it in q:
                            t2=it.text
                        var2=t1.split(t2)[0]
                        tit_vals.append(var2)
                    else:
                        var2=el.text
                        tit_vals.append(var2)
            for index,item in enumerate(tit_names):
                result_list.append((tit_names[index],tit_vals[index]))
            print '%d out of %d processed'%(counter,len(all_links))
            counter+=1
        result_tuple=(main_author,result_list)
        return result_tuple

    def reformat(self,group_by,sort_by):
        global result_tuple
        group_by_none=[]
        list_of_ind=[]
        cnt=0
        curr_ind=result_tuple[1][0][0]
        for item,val in result_tuple[1]:
            if curr_ind==item:
                list_of_ind.append(cnt)
            cnt+=1
        p=0
        for j in range(1,len(list_of_ind)):
            temp_list=[]
            for i in range(p,len(result_tuple[1])):
                if (list_of_ind[j]-list_of_ind[j-1])>len(temp_list):
                    temp_list.append(result_tuple[1][i])
            p+=len(temp_list)
            group_by_none.append(temp_list)
        temp_list2=[]
        for k in range(list_of_ind[-1],len(result_tuple[1])):
            temp_list2.append(result_tuple[1][k])
        group_by_none.append(temp_list2)

        def cit_sorter(dictionary):
            comm=re.compile('\w+\s*\w+\s*(\d+)')
            sort_by_cit=[]
            for item in dictionary.items():
                temp_sort=[]
                all_cit_count=[]
                for el in item[1]:
                    for tit,sub in el:
                        if tit.lower() =='total citations':
                            match=re.search(comm,sub)
                            cit=int(match.group(1))
                            all_cit_count.append(cit)
                while len(item[1])!=len(all_cit_count):
                    all_cit_count.append(0)  # For the links with no citation count
                all_cit_count.sort(reverse=True)
                for ccount in all_cit_count:
                    for el in item[1]:
                        for tit2,sub2 in el:
                            popo=ccount
                            if tit2.lower()=='total citations':
                                match2=re.search(comm,sub2)
                                cit=int(match2.group(1))
                                if popo == cit:
                                    temp_sort.append(el)
                            elif ccount==0:
                                temp_sort.append(el)
                #print all_cit_count
                sort_by_cit.append((item[0],temp_sort))
            return sort_by_cit
        #Now we have a list of group by none with all our links grouped in no order
        #We now attempt to create the group by year grouping

        def year_grouping(listed):
            group_by_year={}
            for item in listed:
                for ind,value in item:
                    if ind == 'Publication date':
                        yr=int(value[0:4])
                        if yr not in group_by_year:
                            group_by_year[yr]=[item]
                        else:
                            group_by_year[yr].append(item)
            return group_by_year

        if group_by.lower()=='year':
            group_by_year=year_grouping(group_by_none)
            #print group_by_year.items()
            if sort_by.lower()=='year':
                sort_by_year=group_by_year.items()
                sort_by_year.sort(reverse=True)
                return sort_by_year
            else:
                result=cit_sorter(group_by_year)
                return result
        elif group_by.lower()=='type':
            group_by_type={}
            doc_types=['journal','conference','patent office','book']
            for item in group_by_none:
                for ind,value in item:
                    if ind.lower() in doc_types:
                        if ind not in group_by_type:
                            group_by_type[ind]=[item]
                        else:
                            group_by_type[ind].append(item)
            if sort_by.lower()=='year':
                sort_by_year={}
                for typ,element in group_by_type.items():
                    sort_by_year.setdefault(typ,[])
                    temp=year_grouping(element)
                    temp2=temp.items()
                    temp2.sort(reverse=True)
                    sort_by_year[typ].append(temp2)
                sort_by_year=sort_by_year.items()
                return sort_by_year

            else:
                res=cit_sorter(group_by_type)
                return res
        else:
            if sort_by.lower()=='year':
                gby=[]
                sort_by_year=[]
                #sort_by_year.sort(reverse=True)
                #print sort_by_year
                for item in group_by_none:
                    for sub,el in item:
                        if sub.lower()=='publication date':
                            gby.append(int(el[0:4]))
                gby.sort(reverse=True)
                for yr in gby:
                    for item in group_by_none:
                        for sub,el in item:
                            if sub.lower()=='publication date':
                                year=int(el[0:4])
                                if item not in sort_by_year and year==yr:
                                    sort_by_year.append(item)
                                    break
                return sort_by_year

            else:
                #Continue with this part later
                output_dict={'Results':group_by_none}
                finres=cit_sorter(output_dict)
                return finres


#fetcher=GoogleScholarFetcher('http://engr212.byethost10.com/Scholar%20-%20Ahmet%20Bulut/scholar.google.com/citations2085.html')
#fetcher.fetch()
#fetcher.reformat('typ','yeoar')




class App(object):
    def __init__(self,master):
        master.title('A JCK PRODUCTION')
        frame1=Frame(master)
        frame1.pack()
        frame2=Frame(master)
        frame2.pack(anchor=W)
        frame3=Frame(frame2)
        frame3.pack(anchor=E)
        frame4=Frame(master)
        frame4.pack(anchor=W)
        frame5=Frame(frame4)
        frame5.pack(anchor=W,side=BOTTOM)
        frame6=Frame(frame5)
        frame6.pack(side=RIGHT)
        frame7=Frame(frame6)
        frame7.pack(anchor=W,side=BOTTOM)
        frame8=Frame(frame6)
        frame8.pack(anchor=E,side=RIGHT,padx=90)
        frame9=Frame(frame8)
        frame9.pack(side=BOTTOM)
        #frame10=Frame(frame5)
        #frame10.pack(side=BOTTOM,anchor=W,padx=10)
        frame11=Frame(master)
        frame11.pack(anchor=W,padx=50)
        frame12=Frame(master)
        frame12.pack(side=LEFT)
        self.frame5=frame5
        w1 = Label(frame1, text='________'*23)
        w1.pack()
        w2 = Label(frame1, text= 'Publication Analyzer-V2.0-(Ltd Edition)', font='Helvetica 15 bold',
                        width=51,fg='black')
        w2.pack()
        w3 = Label(frame1, text='________'*23)
        w3.pack()
        #Now for the entry widgets
        w4=Label(frame1,text='Please enter Google Scholar profile URLs(one URL per line):',
                      font='Verdana 11 italic',fg='red')
        w4.pack(side=LEFT,pady=10)
        self.b1=Button(frame1,text='Download Publication Profiles',font='Helvetica 12 italic',
                       fg='red',bg='white',width=40,height=2,command=self.get_input)
        self.b1.pack(padx=10)
        self.t1=Text(frame2,width=54,height=10)
        self.t1.pack(side=LEFT,padx=10)
        self.lb=Listbox(frame2,width=55)
        self.lb.pack(side=RIGHT,padx=60)
        self.w5=Label(frame3,text='Current Progress: 0.0%',font='Helvetica 11 italic',fg='blue')
        self.w5.pack(side=LEFT)
        self.progressbar = ttk.Progressbar(frame3,orient=HORIZONTAL, length=200, mode='determinate')
        self.progressbar.pack(pady=10,padx=30)

        #Next set of of labels and buttons
        self.w6=Label(frame4,text='View Publications for a researcher:',font='Verdana 12 bold ',fg='brown')
        self.w6.pack(side=LEFT,pady=1)
        self.w7=Label(frame5,text='Choose a\n researcher:',font='Helvetica 11',fg='black',justify=CENTER)
        self.w7.pack(side=LEFT)
        self.combo()
        self.w8=Label(frame6,text='Group by:',font='TimesNewRoman')
        self.w8.pack(side=LEFT)
        #creation of radio buttons
        self.v = IntVar()  # Radio button variable
        self.v.set(3)
        self.rb1=Radiobutton(frame6,text='Year',variable=self.v,value=1,font='Times 10',command=self.gby_sby_fun).pack()
        self.rb2=Radiobutton(frame6,text='Type',variable=self.v,value=2,font='Times 10',command=self.gbt_sby_fun).pack()
        self.rb3=Radiobutton(frame6,text='None',variable=self.v,value=3,font='Times 10',command=self.gbn_sby_fun).pack()
        self.w9=Label(frame7,text='Sort by:',font='TimesNewRoman')
        self.w9.pack(side=LEFT,pady=10,padx=7)
        self.v2=IntVar()
        self.v2.set(1)
        self.rb4=Radiobutton(frame7,text='Year.',variable=self.v2,value=1,font='Times 10',
                             command=self.sby_fun).pack()
        self.rb5=Radiobutton(frame7,text='Cit.C',variable=self.v2,value=2,font='Times 10',
                             command=self.sbc_fun).pack()

        self.L1=Label(frame4,text='Cluster Researchers:',font='Verdana 12 bold',fg='brown')
        self.L1.pack(pady=1,padx=130)
        self.L2=Label(frame8,text='Clustering methods:',font='Times 13 bold')
        self.L2.pack()
        self.v3=IntVar()
        self.v3.set(1)
        self.rb6=Radiobutton(frame8,text='Hierarchical****',variable=self.v3,value=1,font='Times 10',
                             command=self.hierarchical).pack()
        self.rb7=Radiobutton(frame9,text='K-Means',variable=self.v3,value=2,font='Times 10',
                             command=self.kclusterer).pack(side=LEFT)
        self.L3=Label(frame9,text='K:',font='Times 12').pack(side=LEFT)
        self.t2=Text(frame9,width=2,height=1)
        self.t2.pack(side=LEFT)
        self.b2=Button(frame11,text='List Publications',font='Helvetica 12 italic',width=20,height=1,
                       fg='darkgreen',bg='black',command=self.print_publications)
        self.b2.pack(side=LEFT,padx=110)
        self.b3=Button(frame11,text='View Clusters',font='Helvetica 12 italic',width=20,height=1,
                       fg='darkgreen',bg='black',command=self.view_clusters)
        self.b3.pack()
        self.t3=Text(frame12,width=115,height=9)
        self.scrollbar=Scrollbar(frame12,command=self.t3.yview)
        self.scrollbar.pack(side=RIGHT,fill=Y)
        self.t3.config(yscrollcommand=self.scrollbar.set)
        self.t3.pack(pady=5)

    def get_input(self):
        all_data=[]
        tracker=0
        self.gbn_sby=[]
        self.gbn_sbc=[]
        self.gby_sby=[]
        self.gby_sbc=[]
        self.gbt_sby=[]
        self.gbt_sbc=[]
        inpt=self.t1.get("1.0",'end-1c')
        if len(inpt)==0:
            showerror("Error 101", "An error has occurred!"
                               " Please provide a few valid urls")
        else:
            self.progressbar['maximum']=100
            link2use=''
            for char in inpt:
                link2use=link2use+char
            actlink=link2use.split('\n')
            #web=['http://engr212.byethost10.com/Scholar%20-%20Ahmet%20Bulut/scholar.google.com/citations2085.html',
            #'http://engr212.byethost10.com/Scholar%20-%20Ali%20Cakmak/scholar.google.com.tr/citationsdd65.html',
            #'http://engr212.byethost10.com/Scholar%20-%20Hakan%20Dogan/scholar.google.com/citations36e2.html',
            #'http://engr212.byethost10.com/Scholar%20-%20Mehmet%20Serkan%20Apaydin/scholar.google.com/citationsb7b2.html',
            #'http://engr212.byethost10.com/Scholar%20-%20Murat%20Kucukvar/scholar.google.com/citations1173.html',
            #'http://engr212.byethost10.com/Scholar%20-%20Onur%20Guzey/scholar.google.com/citations748c.html']
            len_of_links=len(actlink)
            #Now to initialize the data
            initial_state=['Pending...']*len_of_links
            for item in initial_state:
                self.lb.insert(END,item)
            self.lb.update()
            self.progressbar.start()
            for link in actlink:
                process=None
                fetcher=GoogleScholarFetcher(link)
                self.lb.delete(tracker)
                self.lb.insert(tracker,'Processing...')
                self.lb.update()
                self.progressbar['value']=(tracker*100)/float(len_of_links)
                self.progressbar.update()
                self.w5.config(text='Current Progress: %s%s'%(str(((tracker+1)*100)/float(len_of_links))[0:4],'%'))
                while process!='done':
                    res=fetcher.fetch()
                    self.gbn_sby.append((res[0],fetcher.reformat('None','year')))
                    self.gbn_sbc.append((res[0],fetcher.reformat('None','citation')))
                    self.gby_sby.append((res[0],fetcher.reformat('Year','Year')))
                    self.gby_sbc.append((res[0],fetcher.reformat('year','citation')))
                    self.gbt_sby.append((res[0],fetcher.reformat('type','year')))
                    self.gbt_sbc.append((res[0],fetcher.reformat('type','citation')))
                    self.lb.delete(tracker)
                    self.lb.insert(tracker,str(tracker+1)+'. '+res[0]+' (Downloaded)')
                    process='done'
                    all_data.append(res)
                tracker+=1
            self.progressbar.stop()
            all_names=()
            for name,data in all_data:
                all_names=all_names+(name,)
            self.box['values']=all_names
            self.box.current(len(all_names)-1)
            self.box.update()
            self.b2.config(bg='white')
            self.b3.config(bg='white')
            self.all_data=all_data
            self.gbn_sby_fun()
            self.clicked=1
            self.clst=1
            self.data=[]

    def new_choice(self,event):
        global result_tuple
        if self.box.get()!='None':
            self.viewee=self.box.get()
            for author,details in self.all_data:
                if self.viewee==author:
                    result_tuple=(author,details)
                    if self.sot==0:
                        self.sby_fun()
                    else:
                        self.sbc_fun()



    def combo(self):
        self.box_value=StringVar()
        self.box=ttk.Combobox(self.frame5, textvariable=self.box_value,width=20)
        self.box['values']=('None')
        self.box.current(0)
        self.box.bind("<<ComboboxSelected>>", self.new_choice)
        self.box.pack(side=RIGHT,padx=1)

    def gbn_sby_fun(self):
        self.glob=1
        self.sot=0
        if self.box.get()!='None':
            for author, details in self.gbn_sby:
                if author==result_tuple[0]:
                    print author,details
                    self.finalstuff=details

    def gby_sby_fun(self):
        self.glob=2
        self.sot=0
        if self.box.get()!='None':
            for author, details in self.gby_sby:
                if author==result_tuple[0]:
                    print author,details
                    self.finalstuff=details

    def gbt_sby_fun(self):
        self.glob=3
        self.sot=0
        self.finalstuff=[]
        if self.box.get()!='None':
            temp2=[]
            temp=[]
            temp3={}
            for author, details in self.gbt_sby:
                if author==result_tuple[0]:
                    print author,details
                    temp=details
            for typ,lst in temp:
                for lst2 in lst:
                    for yr,lst3 in lst2:
                        temp2.append((typ,lst3))
            for con,it in temp2:
                for arry in it:
                    if con not in temp3:
                        temp3[con]=[arry]
                    else:
                        temp3[con].append(arry)
            self.finalstuff=temp3.items()

    def sby_fun(self):
        self.sot=0
        if self.glob==1:
            self.gbn_sby_fun()
        elif self.glob==2:
            self.gby_sby_fun()
        elif self.glob==3:
            self.gbt_sby_fun()

#If you first group then sort,it will work

    def sbc_fun(self):
        self.sot=1
        if self.box.get()!='None':
            if self.glob==1:
                for author, details in self.gbn_sbc:
                    if author==result_tuple[0]:
                        print author,details
                        self.finalstuff=details
            elif self.glob==2:
                for author, details in self.gby_sbc:
                    if author==result_tuple[0]:
                        print author,details
                        self.finalstuff=details
            else:
                for author, details in self.gbt_sbc:
                    if author==result_tuple[0]:
                        print author,details
                        self.finalstuff=details

    def print_publications(self):
        dates=['January','February','March','April','May','June','July',
               'August','September','October','November','December']
        def print_style():
            ii=0
            for year,item in self.finalstuff:
                resu=''
                author_last=''
                for list in item:
                    ii+=1
                    for sub,el in list:
                        if sub.lower()=='authors':
                            try:
                                author=el.split(',')
                                author_last=author[0].split()[-1]
                            except:
                                author_last=el.split()[-1]
                            resu=resu+str(ii)+')'+el+'.'
                        elif sub.lower()=='scholar articles':  # Extracting the publication title
                            temp=el.split(author_last)[0]
                            p=len(temp)
                            for i in range(len(temp)-1,len(temp)-4,-1):
                                if temp[i].islower() is False:
                                    p=i
                            temp2=temp[0:p]
                            resu=resu+' '+temp2
                    for sub,el in list:
                        if sub.lower()=='volume':
                            resu=resu+'.'+'vol %s'%str(el)
                        elif sub.lower()=='issue':
                            resu=resu+'.'+'(issue %s)'%str(el)
                        elif sub.lower=='pages':
                            resu=resu+'.'+str(el)
                        elif sub.lower()=='publication date':
                            dt=el.split('/')
                            if len(dt)==1:
                                resu=resu+'. '+str(dt[0])
                            elif len(dt)==2:
                                resu=resu+'. '+dates[int(dt[1])-1]+' ' +str(dt[0])
                            else:
                                resu=resu+'. '+dates[int(int(dt[1])-1)]+' '+str(dt[2])+' '+str(dt[0])+' '
                        elif sub.lower()=='total citations':
                            resu=resu+ ' '+'[%s]'%str(el)
                    resu =resu+'\n'

                out= str(year)+':'+'\n'+resu
                self.t3.insert(END,out)
        if self.clicked==1:
            if self.glob==1 and self.sot==0:
                self.t3.get('1.0',END)
                self.t3.delete('1.0',END)
                self.finalstuff=[('Results',self.finalstuff)]
                print_style()
            else:
                print_style()
            self.clicked=2
        else:
            self.t3.get('1.0',END)
            self.t3.delete('1.0',END)
            if self.glob==1 and self.sot==0:
                self.finalstuff=[('Results',self.finalstuff)]
                print_style()
            else:
                print_style()
            self.clicked=2


    def view_clusters(self):
        pub_types=['journal','conference','book','patent office']
        authors=[]
        word_count={}
        words_all=[]
        lstf=[]
        author_lst=''
        #print self.all_data
        for item in self.all_data:
            lstoftup=[]
            for lst in item[1]:

                if item[0] not in authors:
                    authors.append(item[0])
                    author_lst=item[0].split()[-1]
                for i in range(1,len(lst)):
                    lstoftup.append((lst[i-1],lst[i]))
            lstf.append(lstoftup)
            auth_words=[]
            for el,val in lstoftup:
                if el.lower() in pub_types:
                    auth_words.append(val)
                elif el.lower()=='scholar articles':
                    temp=val.split(author_lst)[0]
                    p=len(temp)
                    for i in range(len(temp)-1,len(temp)-4,-1):
                        if temp[i].islower() is False:
                            p=i
                    temp2=temp[0:p]
                    auth_words.append(temp2)
            words_all.append(auth_words)
        all_words=[]
        for item2 in words_all:
            a_words=[]
            for words in item2:
                words2=re.compile(r'[^A-Z^a-z]+').split(words)
                for word in words2:
                    a_words.append(word)
            all_words.append(a_words)

        complete_word_set=[]
        for itty in all_words:
            for word in itty:
                if word not in complete_word_set:
                    complete_word_set.append(word)
        data=[]
        for item3 in all_words:
            mat={}
            for word2 in item3:
                if word2 not in mat:
                    mat[word2]=1
                else:
                    mat[word2]+=1
            res=[0]*len(complete_word_set)
            for index,vall in enumerate(complete_word_set):
                for wrd in mat:
                    if vall ==wrd:
                        res[index]=mat[vall]
            data.append(res)

        self.data=data
        self.authors=authors
        if self.clst==1:
            self.hierarchical()
        else:
            self.kclusterer()

    def hierarchical(self):
        self.clst=1
        if len(self.data)!=0:
            clust=clusters.hcluster(self.data)
            names=self.authors
            output=clusters.clust2str(clust,names)
            self.t3.get('1.0',END)
            self.t3.delete('1.0',END)
            self.t3.insert(END,output)

    def kclusterer(self):
        self.clst=2
        if len(self.data) !=0:
            self.t3.get('1.0',END)
            self.t3.delete('1.0',END)
            names=self.authors
            val=self.t2.get("1.0",'end-1c')
            if len(val)!=0:
                val=int(val)
                kclust=clusters.kcluster(self.data,k=val)
                #print val
                for i in range(val):
                    a=[names[r] for r in kclust[i]]
                    fin=''
                    for string in a:
                        fin = fin+string+','
                    outpt= '{%s}'%fin+'\n'
                    self.t3.insert(END,outpt)
            else:
                showerror('Error 202','Please input a value for K')







root = Tk()
app = App(root)
root.mainloop()

