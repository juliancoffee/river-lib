let bytes_from filename =
    let file_chan = open_in filename in
    let len = in_channel_length file_chan in
    let byte_buf = Bytes.create len
    in
    really_input file_chan byte_buf 0 len;
    byte_buf
;;

let string_from filename = 
    Bytes.to_string (bytes_from filename)
;;

