---
id: "2026-06-17-claudeでsystemcを書いてみた-01"
title: "ClaudeでSystemCを書いてみた"
url: "https://qiita.com/soldierboy/items/1073f6e86723fa77897e"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-06-17"
date_collected: "2026-06-18"
summary_by: "auto-rss"
query: ""
---

# SystemCのお勉強

- 最近はやりのClaudeで久々にSystemCライブラリーのコードを生成してみた．
- 環境構築もお願いして実施．
- OSはUbunutu24.04．

[Accellera](https://www.accellera.org/downloads/standards/systemc)からC++のライブラリーをダウンロードしビルドする．

プロンプト
```
SystemCをUbuntuにインストールしてお試し実行したい．
```

Claudeが出した手順はそのまま使うとはまりそうだったため，一般的な内容に読み替え．

## 環境構築

`apt`で必要なパッケージソフトウェアをインストールする．

```sh
$ sudo apt update
$ sudo apt install -y build-essential cmake wget
```

`tar.gz`ファイルを解凍し，ビルドする．

```sh
$ tar xvf systemc-2.3.2.tar.gz
$ cd systemc-2.3.2
$ mkdir build
$ cd build
$ cmake .. \
   -DCMAKE_INSTALL_PREFIX=/usr/local/systemc-2.3.2 \
   -DCMAKE_CXX_STANDARD=17 \
   -DCMAKE_BUILD_TYPE=Release
$ make -j$(nproc)
$ sudo make install
```

環境変数を設定する．

```sh
$ echo 'export SYSTEMC_HOME=/usr/local/systemc-2.3.2' >> ~/.bashrc
$ echo 'export LD_LIBRARY_PATH=$SYSTEMC_HOME/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
$ source ~/.bashrc
```

## 実装

### dut_topモジュール

Design側のソースコード．
入力データを20回受け取りそのまま出力する．

```cpp
#ifndef _DUT_TOP_H_
#define _DUT_TOP_H_

#include<systemc.h>
#include<iostream>
using namespace std;

SC_MODULE( dut_top ){

  //----------------------------------
  // port
  //----------------------------------
  sc_in<bool>            clk;
  sc_in<bool>            rst;
  sc_in<bool>            in_vld;
  sc_in<sc_uint<12>>     in_data;
  sc_in<sc_biguint<128>> parameter;
  sc_out<bool>           out_vld;
  sc_out<sc_uint<12>>    out_data;
  sc_out<bool>           done;

  //----------------------------------
  // process
  //----------------------------------
  void procc_main();
  
  SC_CTOR( dut_top )
  {

    SC_CTHREAD( procc_main , clk.pos() );
    reset_signal_is( rst , false );

  }
  
};
#endif // _DUT_TOP_H_
```

```cpp
#include "dut_top.h"

void dut_top::procc_main(){

  cout << "[dut_top] procc_main start" << endl;

  sc_uint<12> r_cnt;
  
  { // reset
    cout << "[dut_top] procc_main start reset" << endl;
    out_vld.write( false );
    out_data.write( 0 );
    r_cnt = 0;
  }

  while( true ){


    bool        w_in_vld;
    bool        w_done;
    sc_uint<12> w_in_data;

    w_in_vld = false;
    w_in_data = 0;
    w_done = false;

    w_in_vld = in_vld.read();
    w_in_data = in_data.read();

    if( w_in_vld ){
      cout << "[dut_top] procc_main start get" << endl;
      cout << "[dut_top] procc_main get enable data_" << r_cnt << endl;
      r_cnt++;
    }

    if( r_cnt == 20 ){
      w_done = true;
    }

    out_vld.write( w_in_vld );
    out_data.write( w_in_data );
    done.write( w_done );
    if( w_in_vld ){
      cout << "[dut_top] procc_main start put" << endl;
    }
    wait();
  }
  
}
```

### main

一番最初に呼ばれる関数．
ここから実行が始まる．

```cpp
#include <systemc.h>
#include "tb_top.h"

int sc_main(int argc, char* argv[]) {

  tb_top tb_top("tb_top");
  sc_clock TB_CLK("TB_CLK",  // 名前
                  10,        // 周期
                  SC_NS,     // 時間単位
                  0.5,       // デューティ比
                  0.0,       // オフセット（double）
                  SC_NS,     // オフセット単位
                  true);     // 最初のエッジposedge
  tb_top.clk(TB_CLK);
  sc_start();
  
  return 0;
}
```

### tb_top

テストベンチの最上位階層．
Designとテストベンチを接続する．

```cpp
#ifndef _TB_TOP_H_
#define _TB_TOP_H_

#include <systemc.h>
#include "tb.h"
#include "dut_top.h"

SC_MODULE( tb_top ){

  //----------------------------------
  // port
  //----------------------------------
  sc_in<bool>  clk;

  //----------------------------------
  // signal
  //----------------------------------
  sc_signal<bool>             s_rst;
  sc_signal<bool>             s_fclk;
  sc_signal<bool>             s_in_vld;
  sc_signal<sc_uint<12>>      s_in_data;
  sc_signal<sc_biguint<128>>  s_parameter;
  sc_signal<bool>             s_out_vld;
  sc_signal<sc_uint<12>>      s_out_data;
  sc_signal<bool>             s_done;
  
  //----------------------------------
  // instance
  //----------------------------------
  tb      *u_tb;
  dut_top *u_dut_top;

  //----------------------------------
  // function
  //----------------------------------
  void func_trace_init();
  void func_trace_close();

  //----------------------------------
  // variable
  //----------------------------------
  sc_trace_file* tf;

  SC_CTOR( tb_top )
  {
    
    u_tb      = new tb      ( "tb"      );
    u_dut_top = new dut_top ( "dut_top" );

    u_tb      -> clk       ( clk         );
    u_tb      -> fclk      ( s_fclk      );
    u_tb      -> rst       ( s_rst       );
    u_tb      -> in_vld    ( s_in_vld    );
    u_tb      -> in_data   ( s_in_data   );
    u_tb      -> parameter ( s_parameter );
    u_tb      -> out_vld   ( s_out_vld   );
    u_tb      -> out_data  ( s_out_data  );
    u_tb      -> done      ( s_done      );

    u_dut_top -> clk       ( s_fclk      );
    u_dut_top -> rst       ( s_rst       );
    u_dut_top -> in_vld    ( s_in_vld    );
    u_dut_top -> in_data   ( s_in_data   );
    u_dut_top -> parameter ( s_parameter );
    u_dut_top -> out_vld   ( s_out_vld   );
    u_dut_top -> out_data  ( s_out_data  );
    u_dut_top -> done      ( s_done      );

    func_trace_init();
  }

  ~tb_top() {
    func_trace_close();
  }
  
};

#endif // _TB_TOP_H_
```

### tb

テストベンチ．
Desingへのデータの入力と出力の受け取りをする．

```cpp
#include "tb_top.h"

void tb_top::func_trace_init() {

  tf = sc_create_vcd_trace_file("waves");

  sc_trace( tf , clk,         "tb_top.clk");
  sc_trace( tf , s_rst,       "tb_top.rst");
  sc_trace( tf , s_fclk,      "tb_top.fclk");
  sc_trace( tf , s_in_vld,    "tb_top.in_vld");
  sc_trace( tf , s_in_data,   "tb_top.in_data");
  sc_trace( tf , s_parameter, "tb_top.parameter");
  sc_trace( tf , s_out_vld,   "tb_top.out_vld");
  sc_trace( tf , s_out_data,  "tb_top.out_data");
  sc_trace( tf , s_done,      "tb_top.done");

  sc_trace( tf , u_tb->clk,        "tb.clk");
  sc_trace( tf , u_tb->fclk,       "tb.fclk");
  sc_trace( tf , u_tb->rst,        "tb.rst");
  sc_trace( tf , u_tb->clk_enable, "tb.clk_enable");
  sc_trace( tf , u_tb->in_vld,     "tb.in_vld");
  sc_trace( tf , u_tb->in_data,    "tb.in_data");
  sc_trace( tf , u_tb->out_vld,    "tb.out_vld");
  sc_trace( tf , u_tb->out_data,   "tb.out_data");
  sc_trace( tf , u_tb->done,       "tb.done");

  sc_trace( tf , u_dut_top->clk,      "dut_top.clk");
  sc_trace( tf , u_dut_top->rst,      "dut_top.rst");
  sc_trace( tf , u_dut_top->in_vld,   "dut_top.in_vld");
  sc_trace( tf , u_dut_top->in_data,  "dut_top.in_data");
  sc_trace( tf , u_dut_top->out_vld,  "dut_top.out_vld");
  sc_trace( tf , u_dut_top->out_data, "dut_top.out_data");
  sc_trace( tf , u_dut_top->done,     "dut_top.done");
}

void tb_top::func_trace_close() {
  if( tf ){
    sc_close_vcd_trace_file(tf);
    tf = nullptr;
  }
}
```

```cpp
#include "tb.h"

//----------------------------------
// Name:
// Detail:
//----------------------------------
void tb::proct_reset(){
  cout << "[tb] proct_reset start" << endl;

  wait( e_clk   );
  wait();

  parameter_reg = sc_biguint<128>(0);
  rst.write( true  );
  wait(5);
  rst.write( false );
  wait();
  rst.write( true );
  e_reset.notify();
  cout << "[tb] proct_reset end" << endl;
}

//----------------------------------
// Name:
// Detail:
//----------------------------------
void tb::proct_clk_enable(){

  wait(10);
  
  cout << "[tb] proct_clk_enable start" << endl;
  wait( 10 );

  clk_enable.write( true );
  e_clk.notify();
  cout << "[tb] proct_clk_enable end" << endl;
}

//----------------------------------
// Name:
// Detail:
//----------------------------------
void tb::procm_clk_assign(){
  if( clk_enable.read() ){
    fclk.write( clk.read() );
  }else{
    fclk.write( false );
  }
}

//----------------------------------
// Name:
// Detail:
//----------------------------------
void tb::proct_sim_done(){

  wait( e_clk   );
  wait();
  wait( e_reset );
  wait();

  cout << "[tb] proct_sim_done start" << endl;

  while( true ){
    if( done.read() ){
      break;
    }
    wait();
  }

  wait( 10 );  
  sc_stop();  
}

//----------------------------------
// Name:
// Detail:
//----------------------------------
void tb::proct_main_stream(){

  wait( e_clk   );
  wait();
  wait( e_reset );
  wait();
  
  cout << "[tb] proct_main_stream start" << endl;

  parameter.write( parameter_reg );

  for( int i=0; i<20; i++ ){
    cout << "[tb] proct_main_stream put data_" << i << endl;

    in_vld .write( true           );
    in_data.write( sc_uint<12>(i) );
  
    wait();
    in_vld.write( false );
  }
}

//----------------------------------
// Name:
// Detail:
//----------------------------------
void tb::proct_chk_main_stream(){
  
  wait( e_clk   );
  wait();
  wait( e_reset );
  wait();
  
  cout << "[tb] proct_chk_main_stream start" << endl;

  for( int i=0; i<20; i++ ){

    sc_uint<12> w_out_data;
    w_out_data = sc_uint<12>( 0 );

    while( !out_vld.read() ){ wait(); }
    w_out_data = out_data.read();
    cout << "[tb] proct_chk_main_stream get data_" << i << endl;
    
    wait();
  }

}
```

```cpp
#ifndef _TB_H_
#define _TB_H_

#include <systemc.h>

#include<iostream>
using namespace std;

SC_MODULE( tb ){

  //----------------------------------
  // port
  //----------------------------------
  sc_in<bool>             clk;
  sc_out<bool>            fclk;
  sc_out<bool>            rst;
  sc_out<bool>            in_vld;
  sc_out<sc_uint<12>>     in_data;
  sc_out<sc_biguint<128>> parameter;
  sc_in<bool>             out_vld;
  sc_in<sc_uint<12>>      out_data;
  sc_in<bool>             done;

  //----------------------------------
  // signal
  //----------------------------------
  sc_signal<bool>         clk_enable;
  sc_event                e_reset;
  sc_event                e_clk;
  
  //----------------------------------
  // process
  //----------------------------------
  void proct_reset();
  void proct_clk_enable();
  void proct_sim_done();
  void proct_main_stream();
  void proct_chk_main_stream();
  void procm_clk_assign();

  //----------------------------------
  // function
  //----------------------------------

  //----------------------------------
  // variable
  //----------------------------------
  sc_biguint<128> parameter_reg;
  
  SC_CTOR( tb )
  {

    SC_THREAD( proct_reset );
    sensitive << clk.pos();
    
    SC_THREAD( proct_clk_enable );
    sensitive << clk.pos();
    
    SC_THREAD( proct_sim_done );
    sensitive << clk.pos();

    SC_THREAD( proct_main_stream );
    sensitive << clk.pos();

    SC_THREAD( proct_chk_main_stream );
    sensitive << clk.neg();

    SC_METHOD( procm_clk_assign );
    sensitive << clk_enable;
    sensitive << clk;

  }
  
};

#endif // _TB_H_
```

### Makefile

```make
# ============================================================
# Makefile for SystemC Simulation
# 場所: ~/work/LogicLSI/fe/sim/Makefile
# make はこのファイルがある場所で実行すること
# ============================================================

# ------------------------------------------------------------
# SystemC環境設定
# ------------------------------------------------------------
SYSTEMC_HOME  ?= /usr/local/systemc-2.3.2
SYSTEMC_INC    = $(SYSTEMC_HOME)/include
SYSTEMC_LIB    = $(SYSTEMC_HOME)/lib-linux64

# ------------------------------------------------------------
# ディレクトリ定義
# OBJ_DIRは../を含まない単純な名前にする
# ------------------------------------------------------------
SRC_DIRS       = ../src
TB_DIRS        = tb
OBJ_DIR        = obj
TARGET         = DUT

# ------------------------------------------------------------
# ソースファイル収集
# ------------------------------------------------------------
SRC_CPPS       = $(foreach d,$(SRC_DIRS),$(wildcard $(d)/*.cpp))
TB_CPPS        = $(foreach d,$(TB_DIRS), $(wildcard $(d)/*.cpp))
ALL_CPPS       = $(SRC_CPPS) $(TB_CPPS)

# ファイル名だけ取り出してobj/XXX.oにマッピング
OBJS           = $(addprefix $(OBJ_DIR)/,\
                   $(patsubst %.cpp,%.o,$(notdir $(ALL_CPPS))))

# ------------------------------------------------------------
# ヘッダ収集
# ------------------------------------------------------------
ALL_HDRS       = $(foreach d,$(SRC_DIRS) $(TB_DIRS),$(wildcard $(d)/*.h))

# ------------------------------------------------------------
# コンパイラ設定
# ------------------------------------------------------------
CXX      = g++
CXXFLAGS = -std=c++17 -Wall -g \
           -I$(SYSTEMC_INC) \
           $(foreach d,$(SRC_DIRS) $(TB_DIRS),-I$(d))

LDFLAGS  = -L$(SYSTEMC_LIB) \
           -Wl,-rpath=$(SYSTEMC_LIB) \
           -lsystemc -lm

# ============================================================
# ターゲット
# ============================================================

.PHONY: all
all: $(TARGET)

# ------------------------------------------------------------
# リンク
# ------------------------------------------------------------
$(TARGET): $(OBJS)
	@echo "[LINK] $@"
	$(CXX) $(OBJS) $(LDFLAGS) -o $@
	@echo "[DONE] $(TARGET) が生成されました"

# ------------------------------------------------------------
# objディレクトリ生成
# ルールは1つだけ・パターンルールと分離
# ------------------------------------------------------------
$(OBJ_DIR):
	@mkdir -p $@

# ------------------------------------------------------------
# コンパイルルール
# vpathで検索パスを指定しパターンルールを1つに統一
# OBJ_DIRに../が入らないためパターンルールと競合しない
# ------------------------------------------------------------
vpath %.cpp $(SRC_DIRS) $(TB_DIRS)

$(OBJ_DIR)/%.o: %.cpp $(ALL_HDRS) | $(OBJ_DIR)
	@echo "[CC] $<"
	$(CXX) $(CXXFLAGS) -c $< -o $@

# ------------------------------------------------------------
# run
# ------------------------------------------------------------
.PHONY: run
run: $(TARGET)
	@echo "[RUN] シミュレーション開始"
	./$(TARGET)

# ------------------------------------------------------------
# clean
# ------------------------------------------------------------
.PHONY: clean
clean:
	@echo "[CLEAN]"
	rm -f $(TARGET)
	rm -rf $(OBJ_DIR)

# ------------------------------------------------------------
# rebuild
# ------------------------------------------------------------
.PHONY: rebuild
rebuild: clean all

# ------------------------------------------------------------
# デバッグ：変数確認（まずこれで確認する）
# ------------------------------------------------------------
.PHONY: debug
debug:
	@echo "--- ディレクトリ ---"
	@echo "SRC_DIRS = $(SRC_DIRS)"
	@echo "TB_DIRS  = $(TB_DIRS)"
	@echo "OBJ_DIR  = $(OBJ_DIR)"
	@echo "TARGET   = $(TARGET)"
	@echo "--- ソース ---"
	@echo "SRC_CPPS = $(SRC_CPPS)"
	@echo "TB_CPPS  = $(TB_CPPS)"
	@echo "ALL_CPPS = $(ALL_CPPS)"
	@echo "--- オブジェクト ---"
	@echo "OBJS     = $(OBJS)"
	@echo "--- ヘッダ ---"
	@echo "ALL_HDRS = $(ALL_HDRS)"

# ------------------------------------------------------------
# help
# ------------------------------------------------------------
.PHONY: help
help:
	@echo "使い方:"
	@echo "  make         : コンパイル＋リンク"
	@echo "  make run     : コンパイル＋リンク＋実行"
	@echo "  make clean   : 生成物を削除"
	@echo "  make rebuild : clean後にフルビルド"
	@echo "  make debug   : 変数の中身を確認"

```

コンパイルを実行．

```text
$ make
[CC] ../src/dut_top.cpp
g++ -std=c++17 -Wall -g -I/usr/local/systemc-2.3.2/include -I../src -I../include -Itb -Itb/include -c ../src/dut_top.cpp -o obj/dut_top.o
In file included from /usr/local/systemc-2.3.2/include/systemc:118,
                 from /usr/local/systemc-2.3.2/include/systemc.h:219,
                 from ../src/dut_top.h:4,
                 from ../src/dut_top.cpp:1:
/usr/local/systemc-2.3.2/include/sysc/utils/sc_vector.h:290:17: warning: ‘template<class _Category, class _Tp, class _Distance, class _Pointer, class _Reference> struct std::iterator’ is deprecated [-Wdeprecated-declarations]
  290 |   : public std::iterator< std::random_access_iterator_tag
      |                 ^~~~~~~~
In file included from /usr/include/c++/12/bits/stl_algobase.h:65,
                 from /usr/include/c++/12/bits/specfun.h:45,
                 from /usr/include/c++/12/cmath:1935,
                 from /usr/local/systemc-2.3.2/include/systemc.h:45:
/usr/include/c++/12/bits/stl_iterator_base_types.h:127:34: note: declared here
  127 |     struct _GLIBCXX17_DEPRECATED iterator
      |                                  ^~~~~~~~
/usr/local/systemc-2.3.2/include/sysc/utils/sc_vector.h:309:16: warning: ‘template<class _Category, class _Tp, class _Distance, class _Pointer, class _Reference> struct std::iterator’ is deprecated [-Wdeprecated-declarations]
  309 |   typedef std::iterator< std::random_access_iterator_tag, access_type > base_type;
      |                ^~~~~~~~
/usr/include/c++/12/bits/stl_iterator_base_types.h:127:34: note: declared here
  127 |     struct _GLIBCXX17_DEPRECATED iterator
      |                                  ^~~~~~~~
[CC] tb/driver.cpp
g++ -std=c++17 -Wall -g -I/usr/local/systemc-2.3.2/include -I../src -I../include -Itb -Itb/include -c tb/driver.cpp -o obj/driver.o
[CC] tb/main.cpp
g++ -std=c++17 -Wall -g -I/usr/local/systemc-2.3.2/include -I../src -I../include -Itb -Itb/include -c tb/main.cpp -o obj/main.o
In file included from /usr/local/systemc-2.3.2/include/systemc:118,
                 from /usr/local/systemc-2.3.2/include/systemc.h:219,
                 from tb/main.cpp:1:
/usr/local/systemc-2.3.2/include/sysc/utils/sc_vector.h:290:17: warning: ‘template<class _Category, class _Tp, class _Distance, class _Pointer, class _Reference> struct std::iterator’ is deprecated [-Wdeprecated-declarations]
  290 |   : public std::iterator< std::random_access_iterator_tag
      |                 ^~~~~~~~
In file included from /usr/include/c++/12/bits/stl_algobase.h:65,
                 from /usr/include/c++/12/bits/specfun.h:45,
                 from /usr/include/c++/12/cmath:1935,
                 from /usr/local/systemc-2.3.2/include/systemc.h:45:
/usr/include/c++/12/bits/stl_iterator_base_types.h:127:34: note: declared here
  127 |     struct _GLIBCXX17_DEPRECATED iterator
      |                                  ^~~~~~~~
/usr/local/systemc-2.3.2/include/sysc/utils/sc_vector.h:309:16: warning: ‘template<class _Category, class _Tp, class _Distance, class _Pointer, class _Reference> struct std::iterator’ is deprecated [-Wdeprecated-declarations]
  309 |   typedef std::iterator< std::random_access_iterator_tag, access_type > base_type;
      |                ^~~~~~~~
/usr/include/c++/12/bits/stl_iterator_base_types.h:127:34: note: declared here
  127 |     struct _GLIBCXX17_DEPRECATED iterator
      |                                  ^~~~~~~~
[CC] tb/tb.cpp
g++ -std=c++17 -Wall -g -I/usr/local/systemc-2.3.2/include -I../src -I../include -Itb -Itb/include -c tb/tb.cpp -o obj/tb.o
In file included from /usr/local/systemc-2.3.2/include/systemc:118,
                 from /usr/local/systemc-2.3.2/include/systemc.h:219,
                 from tb/tb.h:4,
                 from tb/tb.cpp:1:
/usr/local/systemc-2.3.2/include/sysc/utils/sc_vector.h:290:17: warning: ‘template<class _Category, class _Tp, class _Distance, class _Pointer, class _Reference> struct std::iterator’ is deprecated [-Wdeprecated-declarations]
  290 |   : public std::iterator< std::random_access_iterator_tag
      |                 ^~~~~~~~
In file included from /usr/include/c++/12/bits/stl_algobase.h:65,
                 from /usr/include/c++/12/bits/specfun.h:45,
                 from /usr/include/c++/12/cmath:1935,
                 from /usr/local/systemc-2.3.2/include/systemc.h:45:
/usr/include/c++/12/bits/stl_iterator_base_types.h:127:34: note: declared here
  127 |     struct _GLIBCXX17_DEPRECATED iterator
      |                                  ^~~~~~~~
/usr/local/systemc-2.3.2/include/sysc/utils/sc_vector.h:309:16: warning: ‘template<class _Category, class _Tp, class _Distance, class _Pointer, class _Reference> struct std::iterator’ is deprecated [-Wdeprecated-declarations]
  309 |   typedef std::iterator< std::random_access_iterator_tag, access_type > base_type;
      |                ^~~~~~~~
/usr/include/c++/12/bits/stl_iterator_base_types.h:127:34: note: declared here
  127 |     struct _GLIBCXX17_DEPRECATED iterator
      |                                  ^~~~~~~~
[CC] tb/tb_top.cpp
g++ -std=c++17 -Wall -g -I/usr/local/systemc-2.3.2/include -I../src -I../include -Itb -Itb/include -c tb/tb_top.cpp -o obj/tb_top.o
In file included from
