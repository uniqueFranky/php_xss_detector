package main

import (
	"encoding/json"
	"fmt"
	"github.com/gorilla/mux"
	"github.com/wuwenbao/gcors"
	"io/ioutil"
	"math/rand"
	"net/http"
	"os/exec"
	"strconv"
	"strings"
	"time"
)

type Server struct {
	*mux.Router
}

func main() {
	server := Server{mux.NewRouter()}
	cors := gcors.New(
		server,
		gcors.WithOrigin("*"),
		gcors.WithMethods("*"),
		gcors.WithHeaders("*"),
	)
	server.HandleFunc("/getASTGraph/{pathRank}", getASTGraph()).Methods("POST")
	server.HandleFunc("/getAttnAndPath/{pathRank}", getAttnAndPath()).Methods("POST")
	http.ListenAndServe(":9999", cors)
}

// 跨域中间件
func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 添加 CORS 头部
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		// 继续处理请求
		next.ServeHTTP(w, r)
	})
}
func getASTGraph() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		pathRank := mux.Vars(r)["pathRank"]
		rand.Seed(time.Now().UnixNano())
		imageID := rand.Intn(10000000)

		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
			http.Error(w, "Failed to read request body", http.StatusInternalServerError)
			return
		}
		// 将请求体内容转换为字符串
		code := string(body)
		fmt.Println(code)
		cmd := exec.Command("python3", "evaluate.py", code, pathRank, strconv.Itoa(imageID))

		out, err := cmd.Output()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		output := string(out)
		lines := strings.Split(output, "\n")
		attn := lines[0]
		path := lines[1]
		fmt.Println(attn)
		fmt.Println(path)
		pdfData, err := ioutil.ReadFile(strconv.Itoa(imageID) + ".pdf")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/pdf")

		// 发送图片数据给客户端
		_, err = w.Write(pdfData)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	}
}

func getAttnAndPath() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		pathRank := mux.Vars(r)["pathRank"]
		rand.Seed(time.Now().UnixNano())
		imageID := rand.Intn(10000000)

		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
			http.Error(w, "Failed to read request body", http.StatusInternalServerError)
			return
		}
		// 将请求体内容转换为字符串
		code := string(body)

		cmd := exec.Command("python3", "evaluate.py", code, pathRank, strconv.Itoa(imageID))

		out, err := cmd.Output()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		output := string(out)
		lines := strings.Split(output, "\n")
		w.Header().Set("Content-Type", "application/json")
		if err = json.NewEncoder(w).Encode(lines); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}
}
